"""Chaining グラフのオフラインテスト / offline tests for the chaining graph.

``FakeListChatModel`` を注入するので API キーは不要 / no API key needed.
"""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from lg_workflow_patterns.chaining import build_chaining_graph, run_chaining


def test_chaining_returns_second_step_output() -> None:
    # FakeListChatModel は responses を順に返す。outline → "OUTLINE"、write → "PROSE"。
    # FakeListChatModel yields responses in order: outline → "OUTLINE", write → "PROSE".
    model = FakeListChatModel(responses=["OUTLINE", "PROSE"])
    assert run_chaining("リスト内包表記", model=model) == "PROSE"


def test_chaining_graph_threads_state() -> None:
    # 中間状態（outline）もグラフの State に残ることを確認 / the intermediate outline is in the state.
    model = FakeListChatModel(responses=["OUTLINE", "PROSE"])
    final = build_chaining_graph(model).invoke({"topic": "x"})
    assert final["outline"] == "OUTLINE"
    assert final["prose"] == "PROSE"
