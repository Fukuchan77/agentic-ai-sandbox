"""LlamaIndex トラック L03 — イベント & ストリーミング / events & streaming.

Workflows の強みの 1 つが**ストリーミング**。ステップの途中で ``ctx.write_event_to_stream(...)``
を呼ぶと、呼び出し側は ``handler.stream_events()`` で**逐次**イベントを受け取れます（UI/SSE に好適）。

A key strength of Workflows is **streaming**: call ``ctx.write_event_to_stream(...)`` inside a step
and the caller can consume events **incrementally** via ``handler.stream_events()`` (great for UI/SSE).

    StartEvent ─▶ count ─(TickEvent をストリームへ)─▶ StopEvent
"""

from __future__ import annotations

from collections.abc import Callable

from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)


class TickEvent(Event):
    """ストリームに流す進捗イベント / a progress event written to the stream."""

    msg: str


class CountdownWorkflow(Workflow):
    """n からカウントダウンしながら各ステップを stream する / streams a countdown."""

    @step
    async def count(self, ctx: Context, ev: StartEvent) -> StopEvent:
        n = int(getattr(ev, "n", 3))
        for i in range(n, 0, -1):
            # 最終結果を待たずに、途中経過をストリームへ送る / push progress without waiting.
            ctx.write_event_to_stream(TickEvent(msg=f"tick {i}"))
        return StopEvent(result="done")


async def run_countdown(n: int = 3, on_tick: Callable[[str], None] | None = None) -> str:
    """カウントダウンを実行し、各 tick を on_tick に流して最終結果を返す / stream ticks, return result.

    Args:
        n: カウント数 / how many ticks.
        on_tick: 各 ``TickEvent.msg`` を受け取る callable（``print`` 等）/ a callback per tick.
    """
    wf = CountdownWorkflow(timeout=10)
    handler = wf.run(n=n)
    # ストリームを逐次消費する（最終結果を待つ前に届く）/ consume the stream incrementally.
    async for ev in handler.stream_events():
        if isinstance(ev, TickEvent) and on_tick is not None:
            on_tick(ev.msg)
    return await handler


def main() -> None:
    import asyncio

    result = asyncio.run(run_countdown(3, on_tick=lambda m: print("STREAM>", m)))
    print("result:", result)


if __name__ == "__main__":
    main()
