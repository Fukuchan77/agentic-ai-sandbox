"""Lesson 10 — 本番化 / Productionizing: FastAPI + SSE streaming.

学んだエージェントを **Web API** として公開します。2 つのエンドポイント:

We expose an agent as a **web API** with two endpoints:

- ``POST /chat``        … 一括応答 / single JSON response (``await agent.run``).
- ``POST /chat/stream`` … トークンを Server-Sent Events で逐次配信 / stream tokens via SSE.

``create_app(model=...)`` でモデルを注入できるため、テストでは ``TestModel`` を渡して
**ネットワークなし**で API 全体を検証できます。``create_app(model=...)`` injects the
model, so tests pass a ``TestModel`` and exercise the whole API with **no network**.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from sse_starlette.sse import EventSourceResponse

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from pydantic_ai.models import Model


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


def build_agent(model: Model | None = None) -> Agent[None, str]:
    return Agent(
        model=model or get_model(),
        instructions="あなたは簡潔で親切なアシスタントです。",
    )


def create_app(model: Model | None = None) -> FastAPI:
    """アプリを生成する / build the app. ``model`` はテストで差し替え可能 / injectable in tests."""
    app = FastAPI(title="agentic-ai-bootcamp chat API")
    agent = build_agent(model)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat")
    async def chat(req: ChatRequest) -> ChatResponse:
        # 非同期コンテキストでは await agent.run(...) / use await in async handlers.
        result = await agent.run(req.message)
        return ChatResponse(answer=result.output)

    @app.post("/chat/stream")
    async def chat_stream(req: ChatRequest) -> EventSourceResponse:
        async def event_source() -> AsyncIterator[dict[str, str]]:
            # run_stream はトークンを逐次返す / run_stream yields tokens incrementally.
            async with agent.run_stream(req.message) as result:
                async for delta in result.stream_text(delta=True):
                    yield {"event": "token", "data": delta}
            yield {"event": "done", "data": "[DONE]"}

        return EventSourceResponse(event_source())

    return app


# 注意: モジュール読み込み時に実モデルを組み立てない（API キーが無いと失敗するため）。
# uvicorn には --factory を使い、起動時にだけ create_app() を呼ばせる。
# Note: do NOT build the real model at import time (it would fail without a key).
# Use uvicorn's --factory so create_app() runs only at startup:
#   uv run uvicorn "app:create_app" --factory --reload   (from lessons/10-production/)


def main() -> None:
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
