"""LangGraph トラック L03 — Prompt Chaining / Prompt Chaining as a graph.

本体 [Lesson 06](../../../../lessons/06-workflow-patterns/) の ``prompt_chaining`` は、2 つの
``Agent`` の出力を Python で直接受け渡していました。同じ題材（アウトライン→本文）を、
LangGraph では **State を共有する 2 ノードと、それらを結ぶ辺(edge)** として明示的に表現します。

Lesson 06's ``prompt_chaining`` piped one ``Agent`` into the next in plain Python. Here the
*same* task (outline → prose) becomes an **explicit graph**: two LLM nodes sharing a typed
``State``, wired by edges.

    START → outline → write → END
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from langgraph.graph import END, START, StateGraph

from lg_workflow_patterns.chat import ask, get_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.graph.state import CompiledStateGraph


class ChainState(TypedDict, total=False):
    """グラフ全体で共有する状態 / state shared across the graph."""

    topic: str  # 入力 / input.
    outline: str  # outline ノードの成果物 / produced by the outline node.
    prose: str  # write ノードの成果物（最終出力）/ produced by the write node (final output).


def build_chaining_graph(model: BaseChatModel | None = None) -> CompiledStateGraph:
    """アウトライン→本文の直列グラフを組み立てる / build the outline→prose serial graph.

    Args:
        model: 注入する chat model。``None`` なら ``.env`` から構築。テストでは
            ``FakeListChatModel`` を渡せます。Inject a chat model; tests pass a fake.
    """
    m = model or get_chat_model()

    def outline(state: ChainState) -> ChainState:
        return {"outline": ask(m, "与えられた話題の箇条書きアウトラインを作る。", state["topic"])}

    def write(state: ChainState) -> ChainState:
        # ↑ outline ノードの出力を入力に使う（これがチェーン）/ feed the outline into step 2.
        return {"prose": ask(m, "アウトラインを 1 段落の文章にする。", state["outline"])}

    builder = StateGraph(ChainState)
    builder.add_node("outline", outline)
    builder.add_node("write", write)
    builder.add_edge(START, "outline")
    builder.add_edge("outline", "write")
    builder.add_edge("write", END)
    return builder.compile()


def run_chaining(topic: str, model: BaseChatModel | None = None) -> str:
    """グラフを実行して最終本文を返す / run the graph and return the final prose."""
    return build_chaining_graph(model).invoke({"topic": topic})["prose"]


def main() -> None:
    print("chaining:", run_chaining("リスト内包表記"))


if __name__ == "__main__":
    main()
