# Lesson 05 — 可観測性 / Observability

## 学ぶこと / What you'll learn
- なぜエージェントに可観測性が必要か / Why agents need observability
- Logfire とのネイティブ統合（1 行計装）/ Native Logfire integration (one-line instrument)
- 計装を**任意**にして環境を汚さない設計 / Making instrumentation opt-in

## 前提モジュール / Prerequisites
[Lesson 04](../04-testing/README.md)

## 手順 / Steps
```bash
make test

# 計装を有効にして実行（ローカル表示のみ・トークン無しでOK）
# Run with instrumentation (local-only console, no token needed):
LOGFIRE_ENABLED=1 make run FILE=lessons/05-observability/observability.py
```

クラウドにトレースを送るには、[logfire.dev](https://logfire.pydantic.dev/) の
トークンを `.env` の `LOGFIRE_TOKEN` に設定します。
To ship traces to the cloud, set `LOGFIRE_TOKEN` in `.env`.

## ポイント解説 / Key points
- `logfire.instrument_pydantic_ai()` を一度呼ぶと、以後の **すべての** `Agent` 実行が
  自動でトレースされます（モデル呼び出し・ツール呼び出し・トークン使用量・所要時間）。
  Call it once and **every** subsequent `Agent` run is traced automatically
  (model calls, tool calls, token usage, latency).
- 計装は `LOGFIRE_ENABLED` で**任意**にしています。テストやオフライン学習を妨げず、
  本番でだけ有効化できます。これは「副作用は環境変数で制御する」という実務パターン。
  Instrumentation is gated by `LOGFIRE_ENABLED`, so tests/offline work are never
  blocked — enable it only in production. A practical "side-effects via env" pattern.
- `gen_ai.*` セマンティック規約に沿った OpenTelemetry スパンが出るため、Logfire 以外の
  OTel バックエンドにも流せます。
  It emits OpenTelemetry spans following the `gen_ai.*` conventions, so you can
  also route to non-Logfire OTel backends.

## 演習 / Exercise
1. `LOGFIRE_ENABLED=1` で lesson 03 の天気エージェントを動かし、ツール呼び出しが
   トレースに現れることを確認する。
   Run lesson 03's weather agent with `LOGFIRE_ENABLED=1` and find the tool call.
