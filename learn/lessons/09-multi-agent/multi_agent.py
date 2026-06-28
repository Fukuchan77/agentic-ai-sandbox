"""Lesson 09 — マルチエージェント / Multi-agent (deep research).

複雑な問いは「分割 → 並列調査 → 統合」で解くと強い。これは Agentic AI（複数エージェント
のオーケストレーション）の代表例で、lesson 06 の orchestrator-workers と parallelization、
lesson 07 のガードレールを**合成**したものです。

Hard questions are best solved by "decompose → research in parallel →
synthesize". This is a hallmark of Agentic AI (multi-agent orchestration),
**composing** orchestrator-workers + parallelization (lesson 06) with the
guardrails of lesson 07.

役割 / Roles:
- lead         … 話題を小問に分解する / decompose the topic into sub-questions.
- researcher   … 各小問を独立に調べる（並列）/ research each sub-question (parallel).
- synthesizer  … 調査結果を 1 つの要約に統合する / merge findings into one summary.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


class SubQuestions(BaseModel):
    """lead の出力 / lead's output."""

    questions: list[str] = Field(description="2〜4 個の小問 / 2-4 sub-questions")


@dataclass
class Finding:
    """1 つの小問への調査結果 / a research result for one sub-question."""

    question: str
    answer: str


@dataclass
class ResearchReport:
    """最終レポート / the final report."""

    findings: list[Finding]
    summary: str


async def deep_research(
    topic: str,
    *,
    lead_model: Model | None = None,
    researcher_model: Model | None = None,
    synth_model: Model | None = None,
    max_parallel: int = 2,
) -> ResearchReport:
    """分割→並列調査→統合 / decompose → parallel research → synthesize.

    Args:
        max_parallel: **ガードレール**。同時に走る researcher の上限（コスト・レート制御）。
            The guardrail: max concurrent researchers (cost / rate control).
    """
    lead = Agent(
        model=lead_model or get_model(),
        output_type=SubQuestions,
        instructions="話題を、独立に調べられる小問 2〜4 個に分解する。",
    )
    researcher = Agent(
        model=researcher_model or get_model(),
        instructions="与えられた小問に、簡潔な事実で答える。",
    )
    synthesizer = Agent(
        model=synth_model or get_model(),
        instructions="複数の調査結果を、矛盾なく 1 段落に統合する。",
    )

    # 非同期コンテキスト内なので run_sync ではなく await run を使う。
    # We are inside an async context, so use `await run`, not `run_sync`.
    sub = (await lead.run(topic)).output

    # 有界並列 / bounded parallelism: セマフォで同時実行数を max_parallel に制限。
    sem = asyncio.Semaphore(max_parallel)

    async def research_one(question: str) -> Finding:
        async with sem:  # ← 同時実行は max_parallel まで / at most max_parallel at once
            result = await researcher.run(question)
            return Finding(question=question, answer=result.output)

    findings = await asyncio.gather(*(research_one(q) for q in sub.questions))

    digest = "\n".join(f"Q: {f.question}\nA: {f.answer}" for f in findings)
    summary = (await synthesizer.run(f"話題: {topic}\n\n{digest}")).output
    return ResearchReport(findings=list(findings), summary=summary)


def main() -> None:
    report = asyncio.run(deep_research("AI エージェントの可観測性"))
    print(f"# {len(report.findings)} findings")
    for f in report.findings:
        print(f"- {f.question} -> {f.answer}")
    print("\nSummary:", report.summary)


if __name__ == "__main__":
    main()
