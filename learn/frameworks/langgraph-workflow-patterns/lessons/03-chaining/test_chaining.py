"""L03 のオフラインテスト / offline tests for L03（API キー不要 / no API key）."""

from __future__ import annotations

from chaining import build_chaining_graph, run_chaining
from langchain_core.language_models.fake_chat_models import FakeListChatModel


def test_chaining_returns_second_step_output() -> None:
    # FakeListChatModel は responses を順に返す。outline → "OUTLINE"、write → "PROSE"。
    # FakeListChatModel yields responses in order: outline → "OUTLINE", write → "PROSE".
    model = FakeListChatModel(responses=["OUTLINE", "PROSE"])
    assert run_chaining("リスト内包表記", model=model) == "PROSE"


def test_chaining_graph_threads_state() -> None:
    model = FakeListChatModel(responses=["OUTLINE", "PROSE"])
    final = build_chaining_graph(model).invoke({"topic": "x"})
    assert final["outline"] == "OUTLINE"
    assert final["prose"] == "PROSE"
