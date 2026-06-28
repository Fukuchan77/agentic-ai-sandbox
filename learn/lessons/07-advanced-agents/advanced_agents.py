"""Lesson 07 — 高度なエージェント / Advanced agent loops.

ここでは **Evaluator-Optimizer** パターンを実装します：生成器が下書きを作り、評価器が
採点とフィードバックを返し、合格点に達するまで（または上限回数まで）改善を繰り返します。

We implement the **Evaluator-Optimizer** pattern: a generator drafts, an
evaluator scores + gives feedback, and we iterate until the draft passes (or we
hit an iteration cap).

実務で最重要なのは **ガードレール**：``max_iters`` で反復を必ず有界にし、暴走と
コスト超過を防ぎます。The most important production concern is the **guardrail**:
``max_iters`` keeps the loop bounded, preventing runaway cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


class Evaluation(BaseModel):
    """評価器の出力 / evaluator output."""

    score: float = Field(ge=0, le=1, description="品質スコア 0..1 / quality score")
    feedback: str = Field(description="改善のための具体的助言 / concrete advice")


@dataclass
class OptimizeResult:
    """最適化ループの結果 / result of the optimize loop."""

    draft: str
    iterations: int
    final_score: float


def evaluator_optimizer(
    task: str,
    *,
    gen_model: Model | None = None,
    eval_model: Model | None = None,
    threshold: float = 0.8,
    max_iters: int = 3,
) -> OptimizeResult:
    """生成⇄評価のループ / Generate ⇄ evaluate loop.

    Args:
        task: 達成したいタスク / the task to accomplish.
        gen_model / eval_model: 生成器・評価器のモデル（テストで個別注入できる）。
            Models for the generator/evaluator (injectable separately in tests).
        threshold: この点以上で合格 / pass at or above this score.
        max_iters: **ガードレール**。反復の上限 / the bounded-loop guardrail.
    """
    generator = Agent(
        model=gen_model or get_model(),
        instructions="タスクに対する下書きを書く。フィードバックがあれば必ず反映する。",
    )
    evaluator = Agent(
        model=eval_model or get_model(),
        output_type=Evaluation,
        instructions="下書きを 0..1 で採点し、改善点を具体的に述べる。",
    )

    feedback = ""
    draft = ""
    evaluation = Evaluation(score=0.0, feedback="")
    iterations = 0

    while iterations < max_iters:  # ← 有界ループ（ガードレール）/ bounded loop
        iterations += 1
        prompt = task if not feedback else f"{task}\n\n前回のフィードバック: {feedback}"
        draft = generator.run_sync(prompt).output
        evaluation = evaluator.run_sync(f"タスク: {task}\n\n下書き:\n{draft}").output
        if evaluation.score >= threshold:
            break
        feedback = evaluation.feedback

    return OptimizeResult(draft=draft, iterations=iterations, final_score=evaluation.score)


def main() -> None:
    result = evaluator_optimizer("初心者向けに『API とは何か』を 3 文で説明する。")
    print(f"iterations={result.iterations} score={result.final_score}")
    print(result.draft)


if __name__ == "__main__":
    main()
