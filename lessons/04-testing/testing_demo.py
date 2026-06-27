"""Lesson 04 — エージェントのテスト / Testing agents.

LLM アプリの最大の不安は「毎回出力が変わること」。Pydantic AI は **2 つの偽モデル**で
これを解決します。

The biggest worry with LLM apps is non-deterministic output. Pydantic AI solves
this with **two fake models**:

- ``TestModel``     … スキーマに沿う出力を自動生成。手早い健全性チェック向き。
                      Auto-generates schema-valid output. Great for quick sanity checks.
- ``FunctionModel`` … あなたが書いた関数で応答を完全制御。ツール呼び出しの分岐など
                      込み入ったシナリオを決定論的に再現できる。
                      You write a function that fully controls the response —
                      replay complex tool-calling flows deterministically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


def build_agent(model: Model | None = None) -> Agent[None, str]:
    """電卓ツールを 1 つ持つエージェント / An agent with a single calculator tool."""
    agent = Agent(
        model=model or get_model(),
        instructions="計算が必要なときは multiply ツールを使ってください。",
    )

    @agent.tool_plain
    def multiply(a: int, b: int) -> int:
        """2 つの整数を掛ける / Multiply two integers."""
        return a * b

    return agent


def calculate(prompt: str, model: Model | None = None) -> str:
    return build_agent(model).run_sync(prompt).output


def main() -> None:
    print(calculate("6 と 7 を掛けて。"))


if __name__ == "__main__":
    main()
