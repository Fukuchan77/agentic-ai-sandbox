"""Lesson 01 — Agent の基礎 / Agent basics.

ここでは 3 つを学びます / Three things here:
1. ``instructions`` でエージェントに役割を与える / give the agent a role.
2. 同期 ``run_sync`` と非同期 ``run`` の使い分け / sync ``run_sync`` vs async ``run``.
3. ``message_history`` で会話を継続する / continue a conversation with ``message_history``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.messages import ModelMessage
    from pydantic_ai.models import Model

INSTRUCTIONS = (
    "あなたは熟練の Python メンターです。"
    "専門用語は避け、初心者にも分かる言葉で、簡潔に答えてください。"
)


def build_agent(model: Model | None = None) -> Agent[None, str]:
    """Python メンターのエージェントを作る / Build a Python-mentor agent."""
    return Agent(model=model or get_model(), instructions=INSTRUCTIONS)


def ask_once(question: str, model: Model | None = None) -> str:
    """同期実行のヘルパ / Synchronous helper."""
    agent = build_agent(model)
    return agent.run_sync(question).output


async def ask_async(question: str, model: Model | None = None) -> str:
    """非同期実行のヘルパ / Asynchronous helper.

    Web サーバ（lesson 10 の FastAPI など）では ``await agent.run(...)`` を使います。
    In a web server (e.g. the FastAPI in lesson 10) you use ``await agent.run(...)``.
    """
    agent = build_agent(model)
    result = await agent.run(question)
    return result.output


def have_conversation(model: Model | None = None) -> list[ModelMessage]:
    """会話履歴を引き継いで複数ターン実行する / Run multiple turns, carrying history.

    ``message_history`` に前ターンの ``result.all_messages()`` を渡すと、
    エージェントは文脈を覚えたまま続きを答えます。

    Passing the previous turn's ``result.all_messages()`` as ``message_history``
    lets the agent answer with the earlier context in mind.
    """
    agent = build_agent(model)
    first = agent.run_sync("リスト内包表記とは何ですか？")
    second = agent.run_sync(
        "それを使った例を一つ見せて。",
        message_history=first.all_messages(),
    )
    return second.all_messages()


def main() -> None:
    print(ask_once("デコレータを一言で説明して。"))


if __name__ == "__main__":
    main()
