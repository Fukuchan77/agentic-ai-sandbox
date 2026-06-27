"""Lesson 00 のオフラインテスト / Offline test for lesson 00.

``TestModel`` を使うと **API キーなし・ネットワークなし** でエージェントを実行できます。
これが Pydantic AI の大きな強みです（詳しくは lesson 04）。

``TestModel`` runs the agent with **no API key and no network**. This is a key
strength of Pydantic AI (see lesson 04 for details).
"""

from __future__ import annotations

from hello_agent import build_agent
from pydantic_ai.models.test import TestModel


def test_agent_returns_text() -> None:
    agent = build_agent(model=TestModel())
    result = agent.run_sync("hello")
    assert isinstance(result.output, str)
    assert result.output  # 空でない / non-empty
