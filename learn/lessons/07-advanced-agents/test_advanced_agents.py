"""Lesson 07 のオフラインテスト / Offline tests for lesson 07.

評価器を ``FunctionModel`` で制御し、ループの停止条件とガードレールを検証します。
We drive the evaluator with ``FunctionModel`` to test the stop condition and the
guardrail deterministically.
"""

from __future__ import annotations

from advanced_agents import evaluator_optimizer
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel


def _evaluator_scoring(score: float) -> FunctionModel:
    """常に固定スコアを返す評価器 / an evaluator that always returns a fixed score.

    出力は構造化（Evaluation）なので、出力ツールを呼ぶ ToolCallPart を返す。
    The output is structured (Evaluation), so we call the output tool.
    """

    def fn(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        tool_name = info.output_tools[0].name  # 構造化出力用のツール名 / the output tool
        args = {"score": score, "feedback": "もっと具体例を"}
        return ModelResponse(parts=[ToolCallPart(tool_name=tool_name, args=args)])

    return FunctionModel(fn)


def test_stops_early_when_score_passes() -> None:
    # 1 回目で 0.95 → threshold 0.8 を超えるので 1 反復で停止。
    # First eval is 0.95 ≥ 0.8, so it stops after a single iteration.
    result = evaluator_optimizer(
        "task",
        gen_model=TestModel(custom_output_text="draft"),
        eval_model=_evaluator_scoring(0.95),
        threshold=0.8,
        max_iters=3,
    )
    assert result.iterations == 1
    assert result.final_score == 0.95


def test_guardrail_caps_iterations() -> None:
    # 常に 0.1（不合格）でも、max_iters=3 で必ず止まる（無限ループしない）。
    # Even with a never-passing 0.1 score, max_iters=3 stops it (no infinite loop).
    result = evaluator_optimizer(
        "task",
        gen_model=TestModel(custom_output_text="draft"),
        eval_model=_evaluator_scoring(0.1),
        threshold=0.8,
        max_iters=3,
    )
    assert result.iterations == 3
    assert result.final_score == 0.1
