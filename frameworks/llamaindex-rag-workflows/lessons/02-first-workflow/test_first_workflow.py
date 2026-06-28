"""L02 のオフラインテスト / offline tests for L02（LLM 不要 / no LLM）."""

from __future__ import annotations

from first_workflow import run_echo


async def test_first_workflow_chains_two_steps() -> None:
    # shout → exclaim の順にイベントが流れる / events flow shout → exclaim.
    assert await run_echo("hello") == "HELLO!"
