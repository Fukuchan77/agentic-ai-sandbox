"""LangGraph トラック L02 — 最初のグラフ / your first graph.

LangGraph の本質は「**State を共有するノード**を、**辺(edge)**でつないだ有向グラフ」です。
ここでは LLM を使わず、純粋な Python のノードだけで**グラフの仕組み**に集中します。

LangGraph is a directed graph of **nodes that share a State**, wired by **edges**. To focus
on the *mechanics*, this lesson uses plain-Python nodes — no LLM yet.

    START → shout → exclaim → END

各ノードは State を読み、**更新分の dict** を返す（LangGraph がマージする）。
Each node reads the State and returns a **partial update** that LangGraph merges in.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from langgraph.graph import END, START, StateGraph

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class GraphState(TypedDict, total=False):
    """グラフ全体で共有する状態 / state shared across the graph."""

    text: str  # 入力 / input.
    loud: str  # shout ノードの成果物 / produced by the shout node.
    result: str  # exclaim ノードの成果物（最終出力）/ produced by exclaim (final output).


def _shout(state: GraphState) -> GraphState:
    """大文字にする / uppercase the text."""
    return {"loud": state["text"].upper()}


def _exclaim(state: GraphState) -> GraphState:
    """感嘆符を付ける / add an exclamation mark."""
    return {"result": state["loud"] + "!"}


def build_first_graph() -> CompiledStateGraph:
    """2 ノードの直列グラフを組み立てる / build a two-node serial graph."""
    builder = StateGraph(GraphState)
    builder.add_node("shout", _shout)
    builder.add_node("exclaim", _exclaim)
    builder.add_edge(START, "shout")
    builder.add_edge("shout", "exclaim")
    builder.add_edge("exclaim", END)
    return builder.compile()


def run_first(text: str) -> str:
    """グラフを実行して最終結果を返す / run the graph and return the final result."""
    final = build_first_graph().invoke({"text": text})
    return final["result"]


def main() -> None:
    graph = build_first_graph()
    print("result:", run_first("hello"))
    # グラフ構造は Mermaid で可視化できる（制御フローがデータになっている証拠）/
    # the structure is drawable as Mermaid — control flow *is* data here.
    print(graph.get_graph().draw_mermaid())


if __name__ == "__main__":
    main()
