# Lesson 06 — ワークフローパターン / Workflow Patterns

## 学ぶこと / What you'll learn
- **Prompt Chaining**: 出力を次の入力へ直列に渡す / pipe output → next input
- **Routing**: 分類器で仕分け→専門家へ振り分け / classify then dispatch
- **Parallelization**: `asyncio.gather` で並列実行→集約 / fan out then aggregate

## 🔬 別フレームワークと比較 / Compare with another framework
このレッスンの Chaining / Routing は **LangGraph の明示的なグラフ**でも書けます。同じ題材を
読み比べると「制御フローをどう表現するか」の違いがよく分かります。
The Chaining / Routing here can also be expressed as **explicit LangGraph graphs** — compare the
same task to see how each framework represents control flow.
👉 [`frameworks/langgraph-workflow-patterns/`](../../frameworks/langgraph-workflow-patterns/README.md)
（全体像は [`docs/framework-comparison.md`](../../../docs/framework-comparison.md)）

## 前提モジュール / Prerequisites
[Lesson 05](../05-observability/README.md)（基礎トラック修了 / foundations complete）

## 手順 / Steps
```bash
make test
make run FILE=lessons/06-workflow-patterns/workflow_patterns.py
```

## ポイント解説 / Key points
- これらは「エージェントの設計図」。**単一の巨大プロンプトに詰め込まず**、小さな
  エージェントを composable に繋ぐと、テストもデバッグも観測もしやすくなります。
  These are agent blueprints. Instead of one giant prompt, compose small agents —
  easier to test, debug, and observe.
- **直交する 2 軸 / Two orthogonal axes** で整理すると理解が進みます（[`docs/concepts.md`](../../../docs/concepts.md)）:
  - Anthropic のワークフロー分類（chaining / routing / parallelization / …）
  - IBM の粒度（**AI Agent** = 単一構成要素 / **Agentic AI** = 複数の協調）
- Routing と Parallelization は構造化出力（lesson 02）と相性が良い：分類結果や集約結果を
  型で固定できます。Routing/parallelization pair well with structured output.

## 演習 / Exercise
1. Parallelization を「多数決（voting）」に変える：3 つの回答を集めて最頻を選ぶ。
   Turn parallelization into voting: gather 3 answers and pick the majority.
2. Routing に新カテゴリ `sales` を追加する / Add a `sales` category to routing.
