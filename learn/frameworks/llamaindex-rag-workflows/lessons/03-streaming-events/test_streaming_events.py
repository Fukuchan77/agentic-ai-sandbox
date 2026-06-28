"""L03 のオフラインテスト / offline tests for L03（LLM 不要 / no LLM）."""

from __future__ import annotations

from streaming_events import run_countdown


async def test_countdown_streams_each_tick() -> None:
    ticks: list[str] = []
    result = await run_countdown(3, on_tick=ticks.append)
    assert result == "done"
    assert ticks == ["tick 3", "tick 2", "tick 1"]  # 逐次・順序どおり / streamed in order.
