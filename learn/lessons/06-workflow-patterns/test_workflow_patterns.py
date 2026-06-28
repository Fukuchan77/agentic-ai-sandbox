"""Lesson 06 のオフラインテスト / Offline tests for lesson 06."""

from __future__ import annotations

from pydantic_ai.models.test import TestModel
from workflow_patterns import parallelization, prompt_chaining, routing


def test_prompt_chaining_runs_two_steps() -> None:
    out = prompt_chaining("topic", model=TestModel(custom_output_text="step output"))
    assert out == "step output"  # 2 段目の出力が返る / step 2's output is returned


def test_routing_dispatches_to_specialist() -> None:
    # 分類器は Route(category=...) を、専門家は文字列を返す。両者で型が違うため
    # TestModel は各エージェントのスキーマに合わせて出力を生成する。
    # The classifier returns Route(...); the specialist returns text. TestModel
    # adapts its output to each agent's schema automatically.
    out = routing("請求の質問です", model=TestModel())
    assert isinstance(out, str) and out


async def test_parallelization_returns_three_angles() -> None:
    results = await parallelization("リモートワーク", model=TestModel(custom_output_text="x"))
    assert len(results) == 3
    assert all(r == "x" for r in results)
