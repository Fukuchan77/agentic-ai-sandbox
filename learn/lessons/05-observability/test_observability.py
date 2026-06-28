"""Lesson 05 のオフラインテスト / Offline tests for lesson 05."""

from __future__ import annotations

import os

from observability import build_agent, configure_observability
from pydantic_ai.models.test import TestModel


def test_disabled_by_default(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # LOGFIRE_ENABLED 未設定なら計装しない（外部依存なしで動く）。
    # Without LOGFIRE_ENABLED, no instrumentation (works with no external deps).
    monkeypatch.delenv("LOGFIRE_ENABLED", raising=False)
    assert configure_observability() is False


def test_agent_runs_regardless_of_observability() -> None:
    # 計装の有無に関わらずエージェントの挙動は同じ / behavior is identical.
    out = build_agent(model=TestModel()).run_sync("hi").output
    assert isinstance(out, str) and out


def test_enabled_flag_is_read(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # 有効化フラグが読まれることだけを確認（実際の送信はしない設定）。
    # Confirm the flag is honored (configured for no network send).
    monkeypatch.setenv("LOGFIRE_ENABLED", "1")
    monkeypatch.delenv("LOGFIRE_TOKEN", raising=False)
    assert os.environ["LOGFIRE_ENABLED"] == "1"
    assert configure_observability() is True
