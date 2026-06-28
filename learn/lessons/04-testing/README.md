# Lesson 04 — エージェントのテスト / Testing Agents

## 学ぶこと / What you'll learn
- `TestModel` で素早く健全性チェック / Quick sanity checks with `TestModel`
- `custom_output_text` / `custom_output_args` / `call_tools` で出力を制御 / Control output
- `FunctionModel` でツール呼び出しの流れを**決定論的に**再現 / Deterministic flows
- `AgentInfo` から登録ツールを検査 / Inspect registered tools via `AgentInfo`

## 前提モジュール / Prerequisites
[Lesson 03](../03-tools-and-deps/README.md)

## 手順 / Steps
```bash
make test
```

## ポイント解説 / Key points
- **なぜ偽モデルか / Why fake models**: 本物の LLM はお金がかかり、遅く、毎回出力が
  変わります。CI で安定して回すには `TestModel` / `FunctionModel` が必須です。
  Real LLMs cost money, are slow, and vary run-to-run. Fakes make CI fast & stable.
- 使い分け / When to use which:
  - `TestModel` … 「動くか？型は合うか？」の確認 / "does it run / typecheck?"
  - `FunctionModel` … 「ツール A を呼んでから B を呼ぶ」等の**分岐シナリオ**の固定 /
    pin **branching scenarios** like "call tool A then B".
- このコースの全テストはこの 2 つだけで完結し、**API キー不要**です。
  Every test in this course uses only these two — **no API key required**.

## 演習 / Exercise
1. `multiply` が呼ばれた引数を記録し、`FunctionModel` で検証する。
   Record the args `multiply` was called with and assert them via `FunctionModel`.
2. ツールが**呼ばれない**ケースを `call_tools=[]` でテストする。
   Test the no-tool path with `call_tools=[]`.
