"""Prompt Chaining を LangGraph のグラフで / Prompt Chaining as a LangGraph graph.

Lesson 06 の ``prompt_chaining`` は、2 つの ``Agent`` の出力を Python で直接受け渡していました
（``lessons/06-workflow-patterns/workflow_patterns.py``）。同じ題材（アウトライン→本文）を、
LangGraph では **State を共有する 2 ノードと、それらを結ぶ辺(edge)** として明示的に表現します。

Lesson 06's ``prompt_chaining`` piped the output of one ``Agent`` into the next in
plain Python. Here the *same* task (outline → prose) becomes an **explicit graph**:
two nodes sharing a typed ``State``, wired by edges.

    START → outline → write → END

Pydantic AI 版との違い / vs. the Pydantic AI version:
- 制御フローが**データ（グラフ）として可視化**できる（``graph.get_graph().draw_mermaid()``）。
- ノード間の受け渡しは戻り値の dict で **State を部分更新**する形になる。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from lg_workflow_patterns.provider import get_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.graph.state import CompiledStateGraph


class ChainState(TypedDict, total=False):
    """グラフ全体で共有する状態 / state shared across the graph.

    各ノードは必要なキーを読み、更新分の dict を返す（LangGraph がマージする）。
    Each node reads what it needs and returns a partial dict that LangGraph merges in.
    """

    topic: str  # 入力 / input.
    outline: str  # outline ノードの成果物 / produced by the outline node.
    prose: str  # write ノードの成果物（最終出力）/ produced by the write node (final output).


def _ask(model: BaseChatModel, system: str, user: str) -> str:
    """1 ターンのチャットを実行して本文テキストを返す / one chat turn → text content."""
    reply = model.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return _content_to_text(reply.content)


def _content_to_text(content: object) -> str:
    """AIMessage.content（str か parts のリスト）を str に正規化する / normalize content to a string.

    LangChain のバージョンにより content は文字列か「テキストパーツのリスト」のどちらか。
    どちらでも壊れないように両対応する。Content may be a string or a list of parts
    depending on the LangChain version; handle both.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "".join(parts)
    return str(content)


def build_chaining_graph(model: BaseChatModel | None = None) -> CompiledStateGraph:
    """アウトライン→本文の直列グラフを組み立てる / build the outline→prose serial graph.

    Args:
        model: 注入する chat model。``None`` なら ``.env`` から構築。テストでは
            ``FakeListChatModel`` を渡せます。Inject a chat model; ``None`` builds one
            from ``.env``. Tests can pass a ``FakeListChatModel``.
    """
    m = model or get_chat_model()

    def outline(state: ChainState) -> ChainState:
        text = _ask(m, "与えられた話題の箇条書きアウトラインを作る。", state["topic"])
        return {"outline": text}

    def write(state: ChainState) -> ChainState:
        # ↑ outline ノードの出力を入力に使う（これがチェーン）/ feed the outline into step 2.
        text = _ask(m, "アウトラインを 1 段落の文章にする。", state["outline"])
        return {"prose": text}

    builder = StateGraph(ChainState)
    builder.add_node("outline", outline)
    builder.add_node("write", write)
    builder.add_edge(START, "outline")
    builder.add_edge("outline", "write")
    builder.add_edge("write", END)
    return builder.compile()


def run_chaining(topic: str, model: BaseChatModel | None = None) -> str:
    """グラフを実行して最終本文を返す / run the graph and return the final prose."""
    graph = build_chaining_graph(model)
    final = graph.invoke({"topic": topic})
    return final["prose"]


def main() -> None:
    print("chaining:", run_chaining("リスト内包表記"))


if __name__ == "__main__":
    main()
