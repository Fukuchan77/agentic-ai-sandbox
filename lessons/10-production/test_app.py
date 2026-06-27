"""Lesson 10 のオフラインテスト / Offline tests for lesson 10.

``TestModel`` を注入して FastAPI アプリ全体を **ネットワークなし** で検証します。
Inject a ``TestModel`` and exercise the whole FastAPI app with **no network**.
"""

from __future__ import annotations

from app import create_app
from fastapi.testclient import TestClient
from pydantic_ai.models.test import TestModel


def _client() -> TestClient:
    return TestClient(create_app(model=TestModel(custom_output_text="こんにちは")))


def test_health() -> None:
    res = _client().get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_chat_returns_answer() -> None:
    res = _client().post("/chat", json={"message": "hi"})
    assert res.status_code == 200
    assert res.json() == {"answer": "こんにちは"}


def test_chat_stream_emits_sse_events() -> None:
    res = _client().post("/chat/stream", json={"message": "hi"})
    assert res.status_code == 200
    body = res.text
    # SSE は "event:" と "data:" 行で構成される / SSE is made of event:/data: lines.
    assert "event: token" in body
    assert "こんにちは" in body
    assert "[DONE]" in body
