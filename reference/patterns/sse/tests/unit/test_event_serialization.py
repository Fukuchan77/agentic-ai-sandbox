"""Unit tests for SSE serialization helpers and the EventSource seam (R2.3, R4.2).

ADR-3 fixes both directions of the wire mapping:

* ``to_sse`` derives the SSE ``event:`` name from the ``type`` discriminator and
  the ``data:`` payload from ``model_dump_json()`` (Req 2.3);
* ``parse_sse_events`` reverses the ``data:`` JSON through
  ``TypeAdapter(SseEvent).validate_json``, letting the discriminator dispatch
  back to the exact contract member -- it never branches on ``event:`` (R4.2).

These tests pin both directions independently, their round-trip, the parser's
tolerance of non-``data:`` wire lines (sse-starlette keepalive comments and
``event:`` lines), and the ``EventSource`` Protocol's structural contract.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from patterns_contracts import (
    CompletedEvent,
    ErrorEvent,
    StepStartedEvent,
    TokenEvent,
    ToolCalledEvent,
)

from patterns_sse.events import EventSource, parse_sse_events, to_sse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from patterns_contracts import SseEvent


def _sample_events() -> list[SseEvent]:
    """Ordered, one-of-each sequence (R4.1 shape: step -> tool* -> token* -> completed)."""
    return [
        StepStartedEvent(step="classify"),
        ToolCalledEvent(tool="search", args_json='{"q":"weather"}'),
        TokenEvent(text="Hel"),
        TokenEvent(text="lo"),
        CompletedEvent(output="Hello"),
        ErrorEvent(message="boom"),
    ]


def _encode(events: list[SseEvent]) -> str:
    """Encode events as an sse-starlette-style ``text/event-stream`` body."""
    chunks: list[str] = []
    for event in events:
        wire = to_sse(event)
        chunks.append(f"event: {wire['event']}\r\ndata: {wire['data']}\r\n\r\n")
    return "".join(chunks)


def test_to_sse_event_name_is_type_discriminator() -> None:
    for event in _sample_events():
        assert to_sse(event)["event"] == event.type


def test_to_sse_data_is_model_dump_json() -> None:
    for event in _sample_events():
        wire = to_sse(event)
        assert wire["data"] == event.model_dump_json()
        assert json.loads(wire["data"]) == event.model_dump()


def test_to_sse_returns_only_event_and_data_keys() -> None:
    assert set(to_sse(TokenEvent(text="x"))) == {"event", "data"}


def test_parse_sse_events_dispatches_by_discriminator() -> None:
    body = (
        "event: step_started\r\n"
        'data: {"type":"step_started","step":"classify"}\r\n\r\n'
        "event: token\r\n"
        'data: {"type":"token","text":"Hi"}\r\n\r\n'
        "event: completed\r\n"
        'data: {"type":"completed","output":"Hi"}\r\n\r\n'
    )
    got = parse_sse_events(body)
    assert got == [
        StepStartedEvent(step="classify"),
        TokenEvent(text="Hi"),
        CompletedEvent(output="Hi"),
    ]
    assert [type(event) for event in got] == [StepStartedEvent, TokenEvent, CompletedEvent]


def test_parse_sse_events_ignores_keepalive_and_event_lines() -> None:
    body = (
        ": ping\r\n\r\n"  # sse-starlette keepalive comment line
        "event: token\r\n"
        'data: {"type":"token","text":"x"}\r\n\r\n'
    )
    assert parse_sse_events(body) == [TokenEvent(text="x")]


def test_round_trip_through_wire_preserves_sequence() -> None:
    events = _sample_events()
    assert parse_sse_events(_encode(events)) == events


def test_parse_sse_events_round_trips_payload_with_u2028() -> None:
    # `model_dump_json()` emits U+2028 (LINE SEPARATOR) / U+2029 literally -- JSON
    # does not escape them -- so a naive `splitlines()` parser would split the
    # single-line `data:` payload mid-token and lose the event. The parser must
    # split on SSE line terminators only, leaving the embedded char intact.
    token = TokenEvent(text="before\u2028middle\u2029after")
    body = _encode([token])
    assert "\u2028" in body  # the hazard is actually present on the wire
    assert parse_sse_events(body) == [token]


def test_parse_sse_events_reassembles_multi_line_data() -> None:
    # The SSE multi-line `data:` convention: a writer that frames a payload across
    # consecutive `data:` lines means "join these with `\n`". The parser is the
    # exact inverse -- it accumulates the lines per event and rejoins with `\n`
    # before validating, never dropping a continuation line. Here the JSON object
    # is split across two `data:` lines; the rejoined `\n` is JSON whitespace
    # between tokens, so it validates back to the same event.
    body = 'event: token\r\ndata: {"type":"token",\r\ndata: "text":"x"}\r\n\r\n'
    assert parse_sse_events(body) == [TokenEvent(text="x")]


def test_parse_sse_events_does_not_split_on_unicode_line_breaks() -> None:
    # `str.splitlines()` splits on \r, \v, \f, U+2028, U+2029, U+0085, etc.; the
    # SSE wire only terminates lines on \r\n, \r, or \n. A `data:` JSON payload
    # carrying any of those other code points must stay one logical event.
    for hazard in ("\u2028", "\u2029", "\x0b", "\x0c", "\x85"):
        event = TokenEvent(text=f"x{hazard}y")
        assert parse_sse_events(_encode([event])) == [event]


def test_parse_sse_events_handles_lf_only_framing() -> None:
    # sse-starlette emits CRLF, but the parser must also accept an LF-only body
    # (split on `\n`, tolerate a trailing `\r` the SSE reader strips per spec).
    body = 'event: token\ndata: {"type":"token","text":"lf"}\n\n'
    assert parse_sse_events(body) == [TokenEvent(text="lf")]


async def test_event_source_protocol_accepts_async_generator() -> None:
    class _Fake:
        async def stream(self, query: str) -> AsyncIterator[SseEvent]:
            yield StepStartedEvent(step=query)

    fake = _Fake()
    assert isinstance(fake, EventSource)
    got = [event async for event in fake.stream("classify")]
    assert got == [StepStartedEvent(step="classify")]
