"""L01 のオフラインテスト / offline tests for L01（API キー不要 / no API key）."""

from __future__ import annotations

from langchain_basics import one_shot
from langchain_core.language_models.fake_chat_models import FakeListChatModel


def test_one_shot_returns_model_text() -> None:
    # FakeListChatModel は渡した応答をそのまま返す / returns the canned response verbatim.
    model = FakeListChatModel(responses=["こんにちは"])
    assert one_shot("system", "user", model=model) == "こんにちは"
