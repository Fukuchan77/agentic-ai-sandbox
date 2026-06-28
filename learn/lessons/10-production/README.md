# Lesson 10 — 本番化 / Productionizing (FastAPI + SSE)

## 学ぶこと / What you'll learn
- エージェントを FastAPI の Web API として公開 / Serve an agent via FastAPI
- `await agent.run(...)` を非同期ハンドラで使う / Async handlers with `await run`
- Server-Sent Events (SSE) でトークンを逐次配信 / Stream tokens via SSE
- `TestClient` + `TestModel` で API 全体を**オフライン**テスト / Offline API tests

## 前提モジュール / Prerequisites
[Lesson 01](../01-first-agent/README.md)（async `run`）, 基礎トラック全般 / the foundations

## 手順 / Steps
```bash
make test

# 開発サーバを起動（--factory で起動時にだけ実モデルを構築）
# Start the dev server (--factory builds the real model only at startup):
cd lessons/10-production
uv run uvicorn "app:create_app" --factory --reload
# 別ターミナルで / in another terminal:
curl -X POST localhost:8000/chat -H 'content-type: application/json' -d '{"message":"こんにちは"}'
curl -N -X POST localhost:8000/chat/stream -H 'content-type: application/json' -d '{"message":"こんにちは"}'
```

## ポイント解説 / Key points
- **`create_app(model=...)` の DI**: モデルを引数で受けることで、本番は `get_model()`、
  テストは `TestModel()` を使えます。アプリ全体がネットワークなしでテスト可能に。
  Injecting the model into `create_app` lets prod use `get_model()` and tests use
  `TestModel()` — the entire app is testable offline.
- **import 時に実モデルを作らない / Don't build the real model at import time**:
  `get_model()` は API キーが無いと失敗し得るため、モジュール先頭で `app = create_app()`
  とはしません。uvicorn の `--factory` で起動時にだけ構築します。
- **SSE**: 体感速度のために、回答を待たずトークン到着順に流します。本番では
  「ステップ開始 / ツール呼び出し / 完了」など型付きイベントに広げると UX が上がります
  （`sse-starlette`）。Stream tokens as they arrive for snappy UX; extend to typed
  step/tool/done events in production.
- 本番では lesson 05 の可観測性、lesson 07 のガードレール（`UsageLimits`）、認証・レート
  制限を必ず併用してください。Pair with observability, guardrails, auth, and rate limits.

## 演習 / Exercise
1. `/chat` を lesson 02 の構造化出力（`output_type`）に変える / return structured output.
2. SSE に「ツール呼び出し」イベントを追加する（`agent.iter` を使う）/ add tool-call events.
