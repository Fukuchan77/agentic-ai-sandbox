"""Lesson 11 — エージェントの評価 / Evaluating agents.

Anthropic「Demystifying evals for AI agents」に沿って、エージェントの実行を
**2 つの軸**で採点する最小グレーダを実装します。

We implement a minimal grader that scores an agent run along **two axes**,
following Anthropic's "Demystifying evals for AI agents":

- **Outcome（成果）** — 最終出力は正しく・十分か / is the final output correct and complete?
- **Behavior（過程）** — そこに至る過程は健全か / was the *process* sound?

設計の要点 / Design points:
- 各次元は **1–5 の離散 rating**、ただし証拠が足りなければ **``None``（Unknown）**。
  Each dimension is a discrete 1–5 rating, or ``None`` (Unknown) when evidence is missing.
- **rationale（根拠）必須** — なぜその点数かを必ず言語化させる。
  A rationale is required — the judge must justify every score.
- 集約は **partial credit を許す float** — Unknown は平均から除外する。
  Aggregation is a partial-credit float; Unknown dimensions are excluded from the mean.
- 採点は **独立した judge**（生成に使ったのとは別モデルを注入）で行い、self-eval バイアスを避ける。
  Grading uses an *independent* judge (inject a model separate from the generator) to
  avoid self-evaluation bias.

> これは学習用の簡約版です。本番品質の契約（``GradeReport`` / ``AxisScore`` / ``Judge``）は
> ``pydantic-ai-sandbox`` の ``patterns/EVAL-GRADERS.md``（Spec 011・main にマージ済）に正本があり、
> 3 パターン（evaluator-optimizer / deep-research / autonomous-agent）で共有・ドリフト検証されます。
> 本番との差分はレッスン README「本番契約との違い」を参照（軸は ``list[AxisScore]``、rating は
> 文字列 ``"1".."5"/"unknown"``、集約はハーネス定義、``Judge[SubjectT]`` 注入シーム）。
> This is a teaching-sized version. The production-grade contract lives in
> ``pydantic-ai-sandbox`` (``patterns/EVAL-GRADERS.md``, merged to main); see the lesson README
> for how it differs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model

#: Unknown を表す番兵 / sentinel meaning "evidence insufficient to score".
UNKNOWN: None = None


class DimensionScore(BaseModel):
    """1 つの評価次元のスコア / score for a single evaluation dimension."""

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="1（悪い）..5（良い）。証拠不足なら None=Unknown / 1..5, or None when unknown.",
    )
    rationale: str = Field(
        min_length=1,
        description="なぜその rating かの根拠（必須）/ why this rating — required.",
    )

    @property
    def normalized(self) -> float | None:
        """1..5 を 0..1 に正規化 / map 1..5 onto 0..1; ``None`` stays ``None``."""
        if self.rating is None:
            return None
        return (self.rating - 1) / 4


def _axis_mean(dimensions: list[DimensionScore]) -> float | None:
    """既知次元だけの平均（partial credit）/ mean over *known* dimensions only.

    全次元が Unknown なら ``None`` を返す（採点不能）。
    Returns ``None`` when every dimension is Unknown (nothing to score).
    """
    known = [d.normalized for d in dimensions if d.normalized is not None]
    return sum(known) / len(known) if known else None


class GradeReport(BaseModel):
    """outcome + behavior の 2 軸グレード / a two-axis grade.

    軸ごとに次元を分離して保持する（Anthropic: 次元の分離 / Unknown / partial credit）。
    Dimensions are kept separated per axis (separation / Unknown / partial credit).
    """

    # --- Outcome 軸（最終成果）/ outcome axis (the final result) ---
    correctness: DimensionScore = Field(description="最終出力は正しいか / is the output correct?")
    completeness: DimensionScore = Field(
        description="タスクを十分に満たすか / does it fully address the task?"
    )

    # --- Behavior 軸（過程）/ behavior axis (the process) ---
    tool_use_discipline: DimensionScore = Field(
        description="ツール選択・呼び出しは適切か / were tools chosen and called appropriately?"
    )
    faithfulness: DimensionScore = Field(
        description="根拠に忠実か（捏造していないか）/ is it grounded, not fabricated?"
    )

    def outcome_score(self) -> float | None:
        """Outcome 軸スコア 0..1 / outcome-axis score in 0..1 (``None`` if all Unknown)."""
        return _axis_mean([self.correctness, self.completeness])

    def behavior_score(self) -> float | None:
        """Behavior 軸スコア 0..1 / behavior-axis score in 0..1 (``None`` if all Unknown)."""
        return _axis_mean([self.tool_use_discipline, self.faithfulness])

    def overall(self) -> float:
        """採点できた軸の平均 / mean of the axes that could be scored.

        どちらの軸も採点できなければ 0.0（証拠ゼロ）/ 0.0 when neither axis is scorable.
        """
        axes = [s for s in (self.outcome_score(), self.behavior_score()) if s is not None]
        return sum(axes) / len(axes) if axes else 0.0


_JUDGE_INSTRUCTIONS = """\
あなたは独立した評価者（judge）です。エージェントの実行を採点してください。
- outcome（最終出力の correctness / completeness）と behavior（tool_use_discipline /
  faithfulness）を分けて 1..5 で採点する。
- 証拠が足りない次元は rating を None（Unknown）にする。推測で埋めない。
- すべての次元に rationale（根拠）を必ず付ける。

You are an independent judge. Score the agent run.
- Score outcome (correctness / completeness) and behavior (tool_use_discipline /
  faithfulness) separately on 1..5.
- Use None (Unknown) when evidence is insufficient — never guess.
- Provide a rationale for every dimension.
"""


def grade_run(
    task: str,
    transcript: str,
    final_output: str,
    *,
    judge_model: Model | None = None,
) -> GradeReport:
    """1 回のエージェント実行を採点する / Grade a single agent run.

    Args:
        task: エージェントに与えたタスク / the task the agent was given.
        transcript: 過程（ツール呼び出し等）/ the process (tool calls, steps).
        final_output: 最終出力 / the final answer.
        judge_model: judge 用モデル。**生成に使ったのとは別モデル**を注入して
            self-eval バイアスを避ける。省略時は ``get_model()``。
            The judge model — inject a model *separate* from the generator to avoid
            self-eval bias. Defaults to ``get_model()``.
    """
    judge = Agent(
        model=judge_model or get_model(),
        output_type=GradeReport,
        instructions=_JUDGE_INSTRUCTIONS,
    )
    prompt = (
        f"タスク / Task:\n{task}\n\n"
        f"過程 / Transcript:\n{transcript}\n\n"
        f"最終出力 / Final output:\n{final_output}"
    )
    return judge.run_sync(prompt).output


def main() -> None:
    report = grade_run(
        task="『API とは何か』を初心者向けに 3 文で説明する。",
        transcript="(ツール呼び出しなし。直接回答)",
        final_output="API は…（3 文の説明）",
    )
    print(f"outcome={report.outcome_score()} behavior={report.behavior_score()}")
    print(f"overall={report.overall():.2f}")


if __name__ == "__main__":
    main()
