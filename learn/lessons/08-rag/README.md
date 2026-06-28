# Lesson 08 — RAG（検索拡張生成）/ Retrieval-Augmented Generation

## 学ぶこと / What you'll learn
- RAG の基本: **検索 → 生成 → 引用検証** / retrieve → generate → verify
- 検索を**ツール**として与える / expose retrieval as a tool
- `output_validator` + `ModelRetry` で**根拠のない引用を弾く** / reject ungrounded citations

## 🔬 別フレームワークと比較 / Compare with another framework
同じ RAG を **LlamaIndex のイベント駆動 Workflows** でも書けます。引用検証の `ModelRetry` が
`RetryEvent` の**ループ**に、途中経過が `stream_events()` の**ストリーミング**に変わります。
The same RAG can be built with **event-driven LlamaIndex Workflows**: `ModelRetry` becomes a
`RetryEvent` loop, and progress is **streamed** via `stream_events()`.
👉 [`frameworks/llamaindex-rag-workflows/`](../../frameworks/llamaindex-rag-workflows/README.md)
（全体像は [`docs/framework-comparison.md`](../../../docs/framework-comparison.md)）

## 前提モジュール / Prerequisites
[Lesson 03](../03-tools-and-deps/README.md)（ツール）, [Lesson 02](../02-structured-output/README.md)（構造化出力）

## 手順 / Steps
```bash
make test
make run FILE=lessons/08-rag/rag.py
```

## ポイント解説 / Key points
- **RAG はワークフローパターンではなく応用レイヤ**。lesson 06 の 6 パターンとは別軸で、
  「外部知識をどう注入するか」を扱います。RAG is an *application layer*, orthogonal to
  the lesson-06 workflow patterns.
- ここでは埋め込みを使わず**キーワード一致**で検索していますが、本物の RAG ではこの
  `retrieve` をベクトル検索に差し替えるだけ。インターフェース（`retrieve(query)->docs`）は
  同じです。Swap `retrieve` for vector search later; the interface is unchanged.
- **引用検証が重要 / Citations matter**: `output_validator` が実在しない ID を見つけると
  `ModelRetry` を投げ、Pydantic AI がモデルにやり直しを促します。これがハルシネーション
  対策の実務的な一手です。The validator raises `ModelRetry` on fake IDs, forcing a
  retry — a practical guard against hallucinated sources.

## 演習 / Exercise
1. `CORPUS` に文書を追加し、`retrieve` の上位結果が変わることを確認する。
   Add documents to `CORPUS` and watch the ranking change.
2. `retrieve` を「タイトル一致を加点」する形に改良する / weight title matches higher.
