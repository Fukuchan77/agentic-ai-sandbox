"""LangGraph トラック L04 — Routing / Routing as conditional edges.

本体 [Lesson 06](../../../../lessons/06-workflow-patterns/) の ``routing`` は、分類器 ``Agent`` の
結果を Python の ``dict`` で引いて専門家 ``Agent`` に渡していました。LangGraph では
**classify ノード → 条件付き辺(conditional edges) → 各専門家ノード** として、分岐そのものを
グラフに刻みます。

    START → classify ─(billing)→  billing  ─→ END
                       ─(technical)→ technical ─→ END
                       ─(other)→    other    ─→ END

題材・カテゴリは本体 Lesson 06 と同一（billing / technical / other）なので 1:1 で比較できます。

オフライン性 / Offline note:
分類は LLM 応答テキストを ``_normalize`` で Category に正規化します。``with_structured_output`` を
使わないので、``FakeListChatModel`` を注入するだけでテストが決定論的に緑になります。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from lg_workflow_patterns.chat import ask, get_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.graph.state import CompiledStateGraph

Category = Literal["billing", "technical", "other"]
_CATEGORIES: tuple[Category, ...] = ("billing", "technical", "other")

# 各専門家の人格 / each specialist's persona — 本体 Lesson 06 と同じ文言。
_SPECIALISTS: dict[Category, str] = {
    "billing": "あなたは請求担当。丁寧に対応する。",
    "technical": "あなたは技術サポート。手順を示す。",
    "other": "あなたは総合窓口。一般的に応対する。",
}


class RouteState(TypedDict, total=False):
    """ルーティンググラフの状態 / state for the routing graph."""

    inquiry: str  # 入力の問い合わせ / the incoming inquiry.
    category: Category  # classify ノードの判定 / decided by the classify node.
    answer: str  # 選ばれた専門家ノードの応答（最終出力）/ the chosen specialist's reply.


def _normalize(text: str) -> Category:
    """LLM の自由文を 3 カテゴリに丸める / map free-form model text to a Category."""
    low = text.lower()
    for cat in _CATEGORIES:
        if cat in low:
            return cat
    return "other"  # 判定不能は総合窓口へ / fall back to the general desk.


def build_routing_graph(model: BaseChatModel | None = None) -> CompiledStateGraph:
    """分類→専門家の分岐グラフを組み立てる / build the classify→specialist branching graph."""
    m = model or get_chat_model()

    def classify(state: RouteState) -> RouteState:
        raw = ask(
            m,
            "問い合わせを billing / technical / other のいずれか 1 語で分類する。",
            state["inquiry"],
        )
        return {"category": _normalize(raw)}

    def make_specialist(cat: Category):
        def specialist(state: RouteState) -> RouteState:
            return {"answer": ask(m, _SPECIALISTS[cat], state["inquiry"])}

        return specialist

    builder = StateGraph(RouteState)
    builder.add_node("classify", classify)
    for cat in _CATEGORIES:
        builder.add_node(cat, make_specialist(cat))

    builder.add_edge(START, "classify")
    # 条件付き辺：classify の判定で次ノードを選ぶ / conditional edges pick the next node.
    builder.add_conditional_edges(
        "classify",
        lambda state: state["category"],
        {cat: cat for cat in _CATEGORIES},
    )
    for cat in _CATEGORIES:
        builder.add_edge(cat, END)
    return builder.compile()


def run_routing(inquiry: str, model: BaseChatModel | None = None) -> str:
    """グラフを実行して専門家の回答を返す / run the graph and return the specialist's answer."""
    return build_routing_graph(model).invoke({"inquiry": inquiry})["answer"]


def main() -> None:
    print("routing:", run_routing("請求書が二重に来ました"))


if __name__ == "__main__":
    main()
