"""Lesson 11 のオフラインテスト / Offline tests for lesson 11.

集約の数学（partial credit / Unknown 除外）は純粋関数として検証し、``grade_run`` は
``FunctionModel`` で judge を固定して検証します。**API キー不要**。
The aggregation math is verified as pure functions; ``grade_run`` is driven by a
``FunctionModel`` judge. No API key required.
"""

from __future__ import annotations

from evals import DimensionScore, GradeReport, grade_run
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


def _dim(rating: int | None) -> DimensionScore:
    return DimensionScore(rating=rating, rationale="because")


def test_partial_credit_excludes_unknown() -> None:
    # correctness=5 (→1.0), completeness=None(Unknown) → outcome = 1.0 (Unknown 除外).
    report = GradeReport(
        correctness=_dim(5),
        completeness=_dim(None),
        tool_use_discipline=_dim(3),  # → 0.5
        faithfulness=_dim(1),  # → 0.0
    )
    assert report.outcome_score() == 1.0
    assert report.behavior_score() == 0.25  # mean(0.5, 0.0)
    assert report.overall() == 0.625  # mean(1.0, 0.25)


def test_axis_is_none_when_all_unknown() -> None:
    report = GradeReport(
        correctness=_dim(None),
        completeness=_dim(None),
        tool_use_discipline=_dim(4),  # → 0.75
        faithfulness=_dim(None),
    )
    assert report.outcome_score() is None  # 採点不能 / unscorable axis
    assert report.behavior_score() == 0.75
    assert report.overall() == 0.75  # 採点できた軸だけの平均


def test_overall_zero_when_no_evidence() -> None:
    allunknown = GradeReport(
        correctness=_dim(None),
        completeness=_dim(None),
        tool_use_discipline=_dim(None),
        faithfulness=_dim(None),
    )
    assert allunknown.overall() == 0.0


def _judge_returning(report: GradeReport) -> FunctionModel:
    """固定の GradeReport を返す judge / a judge that emits a fixed GradeReport."""

    def fn(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        tool_name = info.output_tools[0].name  # 構造化出力ツール / structured-output tool
        return ModelResponse(parts=[ToolCallPart(tool_name=tool_name, args=report.model_dump())])

    return FunctionModel(fn)


def test_grade_run_uses_injected_judge() -> None:
    expected = GradeReport(
        correctness=_dim(4),
        completeness=_dim(3),
        tool_use_discipline=_dim(5),
        faithfulness=_dim(5),
    )
    got = grade_run(
        task="explain APIs",
        transcript="(no tools)",
        final_output="An API is ...",
        judge_model=_judge_returning(expected),
    )
    assert got.correctness.rating == 4
    assert got.faithfulness.rating == 5
    assert got.outcome_score() == 0.625  # mean(0.75, 0.5)
    assert got.behavior_score() == 1.0
