# Lesson 07 — 高度なエージェント / Advanced Agent Loops

## 学ぶこと / What you'll learn
- **Evaluator-Optimizer**: 生成⇄評価のループで品質を上げる / iterate generate ⇄ evaluate
- **ガードレール**: `max_iters` で反復を有界にする / bound the loop with `max_iters`
- 2 つのモデルを別々に注入してループをテストする / inject two models to test the loop

## 前提モジュール / Prerequisites
[Lesson 06](../06-workflow-patterns/README.md)

## 手順 / Steps
```bash
make test
make run FILE=lessons/07-advanced-agents/advanced_agents.py
```

## ポイント解説 / Key points
- 生成器と評価器を **別エージェント**に分けるのが肝。役割が明確になり、評価基準を
  独立して調整・テストできます。Separate generator and evaluator agents; roles
  become clear and the rubric is independently tunable/testable.
- **ガードレールは必須**。LLM ループは放置すると無限／高コストになり得ます。回数上限
  （`max_iters`）・使用量上限（`UsageLimits`）・タイムアウトを必ず入れること。
  Guardrails are mandatory: bound iterations (`max_iters`), usage (`UsageLimits`),
  and time. The test `test_guardrail_caps_iterations` proves the loop terminates.
- これは「自律エージェント（ツールループ＋停止条件）」の縮図でもあります。Pydantic AI の
  `Agent` はツール呼び出しを内部でループしますが、**いつ止めるか**は設計者の責任です。
  This mirrors autonomous agents (tool loop + stopping condition): the `Agent`
  loops tools internally, but *when to stop* is your responsibility.

## 演習 / Exercise
1. `UsageLimits(request_limit=...)` を `run_sync` に渡し、二重のガードレールにする。
   Add `UsageLimits(request_limit=...)` to `run_sync` for a second guardrail.
2. 評価器の出力に `passed: bool` を足し、`score` ではなく `passed` で止める。
   Add `passed: bool` to the evaluator and stop on it instead of `score`.
