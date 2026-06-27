"""L02 のオフラインテスト / offline tests for L02（LLM 不要 / no LLM）."""

from __future__ import annotations

from first_graph import build_first_graph, run_first


def test_first_graph_runs_two_nodes_in_order() -> None:
    # shout → exclaim の順に State が更新される / state flows shout → exclaim.
    assert run_first("hello") == "HELLO!"


def test_first_graph_threads_intermediate_state() -> None:
    final = build_first_graph().invoke({"text": "hi"})
    assert final["loud"] == "HI"  # 中間ノードの成果物も State に残る / intermediate value remains.
    assert final["result"] == "HI!"
