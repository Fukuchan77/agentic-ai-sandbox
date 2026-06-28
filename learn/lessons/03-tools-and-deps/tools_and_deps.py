"""Lesson 03 — ツールと依存性注入 / Tools and dependency injection (DI).

エージェントを「文章を返すだけ」から「**行動する**」存在へ引き上げるのがツールです。
ツールは普通の Python 関数で、第 1 引数に ``RunContext`` を取ると、実行時に注入した
**依存（deps）**へアクセスできます（DB 接続・API クライアント・設定など）。

Tools turn an agent from "text generator" into something that **acts**. A tool
is an ordinary Python function; if its first parameter is a ``RunContext`` it can
reach the **dependencies (deps)** you inject at run time (DB handles, API
clients, config, ...).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic_ai import Agent, RunContext

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


@dataclass
class WeatherDeps:
    """エージェントに注入する依存 / Dependencies injected into the agent.

    本番ではここに実 API クライアントや DB セッションを入れます。学習用に、
    都市→気温の固定辞書を持たせています。

    In production this would hold a real API client or DB session. For learning
    it carries a fixed city→temperature table.
    """

    temperatures: dict[str, int] = field(default_factory=dict)


def get_temperature(ctx: RunContext[WeatherDeps], city: str) -> str:
    """指定都市の気温を返すツール / Tool: return a city's temperature.

    ``ctx.deps`` で注入済みの ``WeatherDeps`` にアクセスします。
    Accesses the injected ``WeatherDeps`` via ``ctx.deps``.
    """
    temp = ctx.deps.temperatures.get(city)
    if temp is None:
        return f"{city} の気温データはありません。 / no data for {city}."
    return f"{city} は {temp}°C です。 / {city} is {temp}°C."


def build_agent(model: Model | None = None) -> Agent[WeatherDeps, str]:
    """気温アシスタント / A weather assistant with one tool."""
    return Agent(
        model=model or get_model(),
        deps_type=WeatherDeps,
        tools=[get_temperature],  # RunContext を取る関数は自動でツール登録される
        instructions=(
            "ユーザーが都市の天気を尋ねたら、必ず get_temperature ツールを使って"
            "気温を調べてから答えてください。推測で答えてはいけません。"
        ),
    )


def ask_weather(question: str, deps: WeatherDeps, model: Model | None = None) -> str:
    return build_agent(model).run_sync(question, deps=deps).output


def main() -> None:
    deps = WeatherDeps(temperatures={"東京": 22, "札幌": 14})
    print(ask_weather("東京の気温は？", deps=deps))


if __name__ == "__main__":
    main()
