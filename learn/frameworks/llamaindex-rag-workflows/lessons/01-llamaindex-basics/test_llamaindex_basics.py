"""L01 のオフラインテスト / offline tests for L01（API キー不要 / no API key）."""

from __future__ import annotations

from llamaindex_basics import one_shot

from li_rag_workflows.testing import ScriptedLLM


async def test_one_shot_returns_llm_text() -> None:
    # ScriptedLLM は script の固定テキストを返す / returns the scripted text verbatim.
    out = await one_shot("any prompt", llm=ScriptedLLM(script="こんにちは"))
    assert out == "こんにちは"
