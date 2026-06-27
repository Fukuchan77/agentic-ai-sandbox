"""Lesson 06 — ワークフローパターン / Workflow patterns.

Anthropic「Building Effective Agents」の中核主張は「複雑なフレームワークより、
**単純で組み合わせ可能なパターン**が成功する」。ここでは代表的な 3 つを、
Pydantic AI の最小プリミティブだけで実装します。

Anthropic's "Building Effective Agents": the most successful builds use
**simple, composable patterns**, not complex frameworks. Here are three, built
from Pydantic AI's minimal primitives:

1. Prompt Chaining   … 出力を次の入力へ直列に渡す / pipe output → next input.
2. Routing           … 分類器が入力を仕分け、専門家に振り分ける / classify then dispatch.
3. Parallelization   … 複数を並列実行して集約する / fan out concurrently, then aggregate.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


# --- 1. Prompt Chaining -------------------------------------------------------
def prompt_chaining(topic: str, model: Model | None = None) -> str:
    """2 段の直列処理: アウトライン → 本文 / Two serial steps: outline → prose."""
    m = model or get_model()
    outliner = Agent(model=m, instructions="与えられた話題の箇条書きアウトラインを作る。")
    writer = Agent(model=m, instructions="アウトラインを 1 段落の文章にする。")

    outline = outliner.run_sync(topic).output
    # ↑ の出力を ↓ の入力へ渡す（これがチェーン）/ feed step 1's output into step 2.
    return writer.run_sync(outline).output


# --- 2. Routing ---------------------------------------------------------------
Category = Literal["billing", "technical", "other"]


class Route(BaseModel):
    """分類結果 / classification result."""

    category: Category


def routing(inquiry: str, model: Model | None = None) -> str:
    """分類器→専門家 / classifier → specialist."""
    m = model or get_model()
    classifier = Agent(
        model=m,
        output_type=Route,
        instructions="問い合わせを billing / technical / other に分類する。",
    )
    specialists: dict[Category, Agent[None, str]] = {
        "billing": Agent(model=m, instructions="あなたは請求担当。丁寧に対応する。"),
        "technical": Agent(model=m, instructions="あなたは技術サポート。手順を示す。"),
        "other": Agent(model=m, instructions="あなたは総合窓口。一般的に応対する。"),
    }
    route = classifier.run_sync(inquiry).output
    return specialists[route.category].run_sync(inquiry).output


# --- 3. Parallelization -------------------------------------------------------
async def parallelization(topic: str, model: Model | None = None) -> list[str]:
    """同じ話題を 3 つの観点で**並列**に評価する / evaluate one topic from 3 angles concurrently."""
    m = model or get_model()
    angles = ["メリット / pros", "デメリット / cons", "リスク / risks"]
    agents = [
        Agent(model=m, instructions=f"次の話題を「{a}」の観点で一言で述べる。") for a in angles
    ]

    # asyncio.gather で同時実行（直列より速い）/ run all at once with asyncio.gather.
    results = await asyncio.gather(*(a.run(topic) for a in agents))
    return [r.output for r in results]


def main() -> None:
    print("chaining:", prompt_chaining("リスト内包表記"))
    print("routing:", routing("請求書が二重に来ました"))
    print("parallel:", asyncio.run(parallelization("リモートワーク")))


if __name__ == "__main__":
    main()
