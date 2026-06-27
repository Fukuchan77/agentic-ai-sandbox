"""Lesson 01 のオフラインテスト / Offline tests for lesson 01."""

from __future__ import annotations

import pytest
from first_agent import ask_async, ask_once, have_conversation
from pydantic_ai.models.test import TestModel


def test_sync() -> None:
    out = ask_once("hello", model=TestModel())
    assert isinstance(out, str) and out


async def test_async() -> None:
    # pytest-asyncio (asyncio_mode=auto) が async テストを実行 / runs async tests.
    out = await ask_async("hello", model=TestModel())
    assert isinstance(out, str) and out


def test_conversation_history_grows() -> None:
    messages = have_conversation(model=TestModel())
    # 2 ターン分のやり取りが履歴に積み上がっている / two turns are accumulated.
    assert len(messages) >= 4


@pytest.mark.parametrize("question", ["a", "b", "c"])
def test_various_inputs(question: str) -> None:
    assert ask_once(question, model=TestModel())
