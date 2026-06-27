"""Lesson 03 のオフラインテスト / Offline tests for lesson 03.

2 通りのテストを示します / Two styles of test:
1. ツール関数を **単体で** 直接呼ぶ（最も簡単）/ call the tool function directly.
2. ``FunctionModel`` で「ツールを呼ぶ→結果を使って答える」流れを **決定論的に**
   再現する / use ``FunctionModel`` to replay the tool-calling flow deterministically.
"""

from __future__ import annotations

from pydantic_ai import RunContext
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.usage import RunUsage
from tools_and_deps import WeatherDeps, ask_weather, build_agent, get_temperature


def test_tool_function_directly() -> None:
    # RunContext を自前で組み立てれば、ツール単体をユニットテストできる。
    # Build a RunContext yourself to unit-test the tool in isolation.
    deps = WeatherDeps(temperatures={"東京": 22})
    ctx: RunContext[WeatherDeps] = RunContext(deps=deps, model=TestModel(), usage=RunUsage())
    assert "22" in get_temperature(ctx, "東京")
    assert "ありません" in get_temperature(ctx, "パリ")


def _scripted(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """1 ターン目: ツール呼び出し / 2 ターン目: ツール結果を文章化."""
    tool_returns = [
        p for m in messages for p in m.parts if getattr(p, "part_kind", None) == "tool-return"
    ]
    if not tool_returns:
        return ModelResponse(
            parts=[ToolCallPart(tool_name="get_temperature", args={"city": "東京"})]
        )
    # ツールが返した内容をそのまま最終回答に含める / echo the tool's result.
    return ModelResponse(parts=[TextPart(content=str(tool_returns[-1].content))])


def test_agent_uses_tool_and_deps() -> None:
    deps = WeatherDeps(temperatures={"東京": 22})
    out = ask_weather("東京の気温は？", deps=deps, model=FunctionModel(_scripted))
    # deps の 22 がツール経由で最終回答に反映されている / the injected 22 flows through.
    assert "22" in out


def test_agent_builds() -> None:
    agent = build_agent(model=FunctionModel(_scripted))
    assert agent is not None
