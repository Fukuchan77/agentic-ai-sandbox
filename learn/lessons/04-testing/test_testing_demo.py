"""Lesson 04 のオフラインテスト / Offline tests for lesson 04.

TestModel と FunctionModel の代表的な使い方を一通り示します。
A tour of the most common TestModel / FunctionModel recipes.
"""

from __future__ import annotations

from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
from testing_demo import build_agent, calculate


def test_testmodel_smoke() -> None:
    # 既定の TestModel は登録ツールを自動で呼び、何らかの出力を返す。
    # Default TestModel auto-calls registered tools and returns some output.
    assert isinstance(calculate("anything", model=TestModel()), str)


def test_testmodel_custom_text() -> None:
    # 最終回答テキストを固定 / pin the final answer text.
    out = calculate("6*7", model=TestModel(custom_output_text="答えは 42 です"))
    assert out == "答えは 42 です"


def test_testmodel_can_skip_tools() -> None:
    # call_tools=[] でツールを呼ばせない / forbid tool calls entirely.
    out = calculate("hi", model=TestModel(call_tools=[], custom_output_text="ok"))
    assert out == "ok"


def _scripted(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """ツールを 1 回呼び、その結果を読んで最終回答を作る決定論シナリオ."""
    tool_returns = [
        p for m in messages for p in m.parts if getattr(p, "part_kind", None) == "tool-return"
    ]
    if not tool_returns:
        return ModelResponse(parts=[ToolCallPart(tool_name="multiply", args={"a": 6, "b": 7})])
    return ModelResponse(parts=[TextPart(content=f"結果は {tool_returns[-1].content} です")])


def test_functionmodel_scripted_tool_flow() -> None:
    out = calculate("6 と 7 を掛けて", model=FunctionModel(_scripted))
    assert "42" in out  # multiply(6,7) == 42 が確実に反映される / deterministically 42


def test_functionmodel_sees_tools_via_agent_info() -> None:
    seen: list[str] = []

    def fn(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        # info からエージェントに登録されたツール一覧を確認できる。
        # info exposes the tools registered on the agent.
        seen.extend(t.name for t in info.function_tools)
        return ModelResponse(parts=[TextPart(content="done")])

    build_agent(model=FunctionModel(fn)).run_sync("hi")
    assert "multiply" in seen
