"""Lesson 08 のオフラインテスト / Offline tests for lesson 08."""

from __future__ import annotations

import pytest
from pydantic_ai import ModelRetry
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from rag import RagAnswer, ask, grounded, retrieve


def test_retrieve_is_deterministic_and_relevant() -> None:
    hits = retrieve("テスト api キー")
    assert any(d.id == "doc-2" for d in hits)  # テスト関連の文書が上位に / test doc surfaces
    assert len(hits) <= 2


def test_grounded_accepts_real_ids() -> None:
    ans = RagAnswer(answer="...", sources=["doc-1"])
    assert grounded(ans) is ans


def test_grounded_rejects_fake_ids() -> None:
    ans = RagAnswer(answer="...", sources=["doc-999"])
    with pytest.raises(ModelRetry):
        grounded(ans)


def _scripted(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """retrieve を 1 回呼び、実在 ID を引用して回答する / call retrieve then cite a real ID."""
    tool_returns = [
        p for m in messages for p in m.parts if getattr(p, "part_kind", None) == "tool-return"
    ]
    if not tool_returns:
        return ModelResponse(
            parts=[ToolCallPart(tool_name="retrieve_docs", args={"query": "test"})]
        )
    out_tool = info.output_tools[0].name
    return ModelResponse(
        parts=[
            ToolCallPart(
                tool_name=out_tool, args={"answer": "TestModel を使う", "sources": ["doc-2"]}
            )
        ]
    )


def test_agent_produces_grounded_answer() -> None:
    result = ask("Pydantic AI をテストするには？", model=FunctionModel(_scripted))
    assert isinstance(result, RagAnswer)
    assert result.sources == ["doc-2"]  # 検証を通過した実在の引用 / a validated, real citation
