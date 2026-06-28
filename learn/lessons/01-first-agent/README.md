# Lesson 01 — はじめてのエージェント / Your First Agent

## 学ぶこと / What you'll learn
- `instructions`（システムプロンプト）で役割を与える / Give a role via `instructions`
- 同期 `run_sync` と 非同期 `run` の違い / `run_sync` vs `await run`
- `message_history` で会話を続ける / Multi-turn conversation with `message_history`

## 前提モジュール / Prerequisites
[Lesson 00](../00-setup/README.md)

## 手順 / Steps
```bash
make test                                            # オフラインテスト / offline tests
make run FILE=lessons/01-first-agent/first_agent.py  # 本物のモデルで / real model
```

## ポイント解説 / Key points
- **`run_sync` vs `run`**: スクリプトや学習中は `run_sync` が手軽。Web サーバなど
  非同期コンテキストでは `await agent.run(...)` を使います（lesson 10）。
  Use `run_sync` for scripts/learning; use `await agent.run(...)` inside async
  contexts such as web servers (lesson 10).
- **会話履歴 / Conversation**: `result.all_messages()` を次の `run` の
  `message_history` に渡すと文脈が引き継がれます。エージェント自身は状態を
  持たない（ステートレス）ので、履歴は呼び出し側が管理します。
  Pass `result.all_messages()` as the next call's `message_history`. The agent
  is stateless; the caller owns the history.

## 演習 / Exercise
1. `INSTRUCTIONS` を書き換えて回答スタイルを変える / Rewrite `INSTRUCTIONS`.
2. `have_conversation` を 3 ターンに拡張する / Extend the conversation to 3 turns.
