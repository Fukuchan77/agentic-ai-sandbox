"""Lesson 00 — Hello, Agent / 環境確認用の最小エージェント.

このレッスンの目的は「環境が正しく組めているか」を確認することだけです。
構造化出力もツールもまだ使いません。``Agent`` を 1 つ作り、1 回走らせます。

The only goal here is to confirm your environment is wired up correctly.
No structured output, no tools yet — just build one ``Agent`` and run it once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


def build_agent(model: Model | None = None) -> Agent[None, str]:
    """最小のエージェントを作る / Build a minimal agent.

    Args:
        model: テスト用にモデルを差し替えるための DI シーム。``None`` のときは
            ``get_model()`` が ``.env`` の設定からモデルを解決します。
            A DI seam to inject a model in tests. When ``None`` the model is
            resolved from ``.env`` via ``get_model()``.
    """
    return Agent(
        model=model or get_model(),
        # instructions は「システムプロンプト」。エージェントの役割を与えます。
        # instructions are the system prompt; they give the agent its role.
        instructions="あなたは親切なアシスタントです。短く一文で答えてください。",
    )


def main() -> None:
    """``.env`` の本物のプロバイダで 1 回実行する / Run once against the real provider."""
    agent = build_agent()
    result = agent.run_sync("Pydantic AI を一言で説明して。")
    print(result.output)


if __name__ == "__main__":
    main()
