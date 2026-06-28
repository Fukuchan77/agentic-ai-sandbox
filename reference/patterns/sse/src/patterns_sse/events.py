r"""SSE serialization helpers and the ``EventSource`` DI seam (Spec 008-2c Req 2.3, 4.2).

ADR-3 fixes the wire mapping in both directions and concentrates it in one place
so the discriminator stays the single source of truth:

* :func:`to_sse` maps an :data:`~patterns_contracts.SseEvent` to its sse-starlette
  ``ServerSentEvent`` kwargs -- ``event:`` is the ``type`` discriminator, ``data:``
  is the member's ``model_dump_json()`` (Req 2.3). No hand-rolled newline-delimited
  ``event:`` / ``data:`` formatting (which would risk SSE-framing edge cases).
* :func:`parse_sse_events` reverses a ``text/event-stream`` body: splitting on the
  SSE line terminators only, it accumulates each event's consecutive ``data:``
  lines (rejoined with ``\n`` per the SSE multi-line convention), then on the
  blank-line event boundary validates the buffer through
  ``TypeAdapter(SseEvent).validate_json``, letting the ``type`` discriminator
  dispatch back to the exact contract member (Req 4.2). It deliberately does
  **not** branch on ``event:`` -- the ``data:`` JSON is authoritative, and
  non-``data:`` framing (keepalive ``:`` comments, ``event:`` / ``id:`` /
  ``retry:`` lines) is ignored.

The lane src stays framework-agnostic (Req 1.3 / NFR-3): this module imports only
the shared contract union via the ``patterns_contracts`` path dependency and the
:class:`~typing.Protocol` seam through which the FastAPI app receives whatever
produces the events (a scripted fake offline, a pydantic-ai adapter in the gated
Ollama integration). It never imports a sibling lane.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from patterns_contracts import SseEvent
from pydantic import TypeAdapter

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

__all__ = ["EventSource", "parse_sse_events", "to_sse"]

# Built once at import time: TypeAdapter compilation is non-trivial, and the
# discriminated union is immutable, so the adapter is shared across calls.
_SSE_EVENT_ADAPTER: TypeAdapter[SseEvent] = TypeAdapter(SseEvent)

# SSE field prefix the reverse mapping consumes. `to_sse` emits single-line JSON
# today, but the parser also reassembles the SSE multi-line `data:` convention.
_DATA_PREFIX = "data:"

# The SSE wire terminates a line on CR LF, a bare CR, or a bare LF -- and only
# those (HTML SSE spec §9.2.4). `str.splitlines()` would additionally split on
# U+000B/U+000C/U+0085/U+2028/U+2029, none of which JSON escapes; since
# `model_dump_json()` can emit e.g. a raw U+2028 inside a string value, splitting
# on those would tear a `data:` payload mid-token. So we split on the SSE
# terminators alone, leaving every other code point intact inside the payload.
_SSE_LINE_BREAK = re.compile(r"\r\n|\r|\n")


@runtime_checkable
class EventSource(Protocol):
    """The DI seam that feeds the SSE app one agent run's events (Req 1.3 / NFR-3).

    Declared as a plain (non-``async``) method returning an ``AsyncIterator`` so
    that an ``async def stream(...)`` async-generator implementation is a
    structural match; an ``async def`` declaration here would instead type the
    member as a coroutine *returning* an iterator, which no generator satisfies.

    Concurrency: one ``EventSource`` is injected for the app's lifetime and
    ``create_app`` calls ``stream`` once per request, so an implementation MUST
    return an independent async generator per call and hold no per-stream state on
    ``self`` that concurrent requests would race (the pydantic-ai adapter is safe
    because ``run_stream_events`` opens a fresh run each call).
    """

    def stream(self, query: str) -> AsyncIterator[SseEvent]:
        """Yield the ordered event sequence for ``query`` (step -> tool* -> token* -> end)."""
        ...


def to_sse(event: SseEvent) -> dict[str, str]:
    """Map an ``SseEvent`` to sse-starlette ``ServerSentEvent`` kwargs (ADR-3, Req 2.3).

    Args:
        event: The contract event to put on the wire.

    Returns:
        ``{"event": <type discriminator>, "data": <model_dump_json()>}`` -- the
        ``event:`` name is the member's ``type``; the ``data:`` payload is its
        JSON serialization.
    """
    return {"event": event.type, "data": event.model_dump_json()}


def parse_sse_events(body: str) -> list[SseEvent]:
    r"""Reverse a ``text/event-stream`` body to the typed event list (ADR-3, Req 4.2).

    This is the exact inverse of the SSE framing :func:`to_sse` feeds sse-starlette.
    The body is split into lines on the SSE terminators only (``\\r\\n`` / ``\\r`` /
    ``\\n``), never via :meth:`str.splitlines`, so a U+2028/U+2029 (or other
    Unicode line break) that ``model_dump_json()`` emits raw inside a string field
    cannot tear a payload mid-token. Lines are then folded per the SSE spec:

    * a ``data:`` line contributes its value (one optional leading space stripped)
      to the current event; consecutive ``data:`` lines accumulate and are rejoined
      with ``\\n`` (the SSE multi-line ``data`` convention);
    * a **blank line** dispatches the accumulated ``data`` buffer -- it is validated
      through ``TypeAdapter(SseEvent).validate_json`` and the ``type`` discriminator
      dispatches it back to the exact contract member;
    * every other line (keepalive ``:`` comments, ``event:`` / ``id:`` / ``retry:``
      framing) is ignored -- the ``data`` JSON is authoritative.

    A trailing event with no terminating blank line is still dispatched, so a body
    that omits the final separator does not silently drop its last event.

    Args:
        body: The buffered ``text/event-stream`` response body.

    Returns:
        The events in wire order, each a concrete member of the ``SseEvent`` union.
    """
    events: list[SseEvent] = []
    data_lines: list[str] = []

    def _dispatch() -> None:
        if data_lines:
            payload = "\n".join(data_lines)
            events.append(_SSE_EVENT_ADAPTER.validate_json(payload))
            data_lines.clear()

    for line in _SSE_LINE_BREAK.split(body):
        if line == "":
            _dispatch()  # blank line is the event boundary (SSE spec)
        elif line.startswith(_DATA_PREFIX):
            # SSE strips a single optional leading space after the colon; the rest
            # of the value is preserved verbatim so embedded whitespace survives.
            value = line[len(_DATA_PREFIX) :]
            data_lines.append(value[1:] if value.startswith(" ") else value)
        # Non-`data:`, non-blank lines (`event:`, `:` comments, ...) are ignored.
    _dispatch()  # flush a trailing event the body left unterminated
    return events
