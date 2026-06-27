"""Lesson 08 — RAG（検索拡張生成）/ Retrieval-Augmented Generation.

RAG は「モデルの知識」に「外部文書」を足して、根拠（引用）付きで答えさせる応用パターン
です。最小構成は **検索 → 生成 → 引用検証** の 3 ステップ。ここでは依存を増やさないため、
埋め込みではなく**決定論的なキーワード一致**で検索します（考え方は本物と同じ）。

RAG augments the model's knowledge with external documents and answers *with
citations*. The minimal shape is **retrieve → generate → verify citations**. To
avoid heavy deps we retrieve via **deterministic keyword overlap** (the idea is
identical to embedding-based retrieval).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


@dataclass(frozen=True)
class Doc:
    """知識ベースの 1 文書 / one document in the knowledge base."""

    id: str
    text: str


# 小さな知識ベース / a tiny knowledge base.
CORPUS: tuple[Doc, ...] = (
    Doc("doc-1", "Pydantic AI は型付き出力と検証を中心に据えた Python のエージェント框架です。"),
    Doc(
        "doc-2", "TestModel と FunctionModel を使うと API キーなしでエージェントをテストできます。"
    ),
    Doc("doc-3", "RAG は検索した文書を文脈に加え、引用付きで回答を生成する手法です。"),
    Doc("doc-4", "ツールは RunContext を第一引数に取ると依存性（deps）へアクセスできます。"),
)

VALID_IDS = frozenset(d.id for d in CORPUS)


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))


def retrieve(query: str, k: int = 2) -> list[Doc]:
    """キーワード一致で上位 k 件を返す / return top-k docs by keyword overlap."""
    q = _tokenize(query)
    scored = sorted(CORPUS, key=lambda d: len(q & _tokenize(d.text)), reverse=True)
    # 重なりが 0 の文書は除外 / drop docs with zero overlap.
    return [d for d in scored if q & _tokenize(d.text)][:k]


class RagAnswer(BaseModel):
    """根拠付きの回答 / a grounded answer."""

    answer: str = Field(description="ユーザーへの回答 / the answer")
    sources: list[str] = Field(description="引用した文書 ID のリスト / cited document IDs")


def grounded(answer: RagAnswer, valid_ids: frozenset[str] = VALID_IDS) -> RagAnswer:
    """引用が実在の文書を指しているか検証する / verify every citation is real.

    Raises:
        ModelRetry: 実在しない ID を引用していた場合。Pydantic AI はこの例外を捕らえ、
            モデルに**やり直し**を促します。If a source ID is not real; Pydantic AI
            catches this and asks the model to **retry**.
    """
    bad = [s for s in answer.sources if s not in valid_ids]
    if bad:
        raise ModelRetry(f"存在しない引用 ID です / unknown source IDs: {bad}")
    return answer


def build_agent(model: Model | None = None) -> Agent[None, RagAnswer]:
    """RAG エージェント / a RAG agent with a retrieval tool + citation guard."""
    agent = Agent(
        model=model or get_model(),
        output_type=RagAnswer,
        instructions=(
            "必ず retrieve_docs ツールで関連文書を検索し、その内容だけに基づいて答えてください。"
            "回答の根拠にした文書の ID を sources に必ず入れてください。"
        ),
    )

    @agent.tool
    def retrieve_docs(ctx: RunContext[None], query: str) -> str:
        """知識ベースを検索する / search the knowledge base."""
        hits = retrieve(query)
        if not hits:
            return "(該当なし / no matches)"
        return "\n".join(f"[{d.id}] {d.text}" for d in hits)

    # 出力バリデータ：引用が実在することを保証する / output validator: ensure citations are real.
    @agent.output_validator
    def _validate(ctx: RunContext[None], output: RagAnswer) -> RagAnswer:
        return grounded(output)

    return agent


def ask(question: str, model: Model | None = None) -> RagAnswer:
    return build_agent(model).run_sync(question).output


def main() -> None:
    result = ask("Pydantic AI をテストするには？")
    print(result.answer)
    print("sources:", result.sources)


if __name__ == "__main__":
    main()
