# LlamaIndex 版 — イベント駆動 RAG / Event-driven RAG with LlamaIndex Workflows

[Lesson 08](../../lessons/08-rag/README.md) の RAG（**検索 → 生成 → 引用検証**）を、Pydantic AI の
エージェントループではなく **LlamaIndex のイベント駆動 Workflows** で書き直した、**完全に独立した**
比較トラックです。途中経過の**ストリーミング**と、検証失敗時の**再検索ループ**（複雑パイプライン）を
体験できます。

A **standalone** comparison track that rewrites Lesson 08's RAG (**retrieve → generate →
verify**) as **event-driven LlamaIndex Workflows** — with **streaming** of intermediate
events and an event-driven **retry loop** on ungrounded citations.

## 学ぶこと / What you'll learn
- **イベント駆動 / Event-driven**: 各 `@step` が `Event` を受けて `Event` を返す疎結合パイプライン
  （[`workflow.py`](src/li_rag_workflows/workflow.py)）。
- **ストリーミング / Streaming**: `Context.write_event_to_stream` + `handler.stream_events()` で
  進捗・トークンを逐次取り出す（SSE/UI に好適）。
- **複雑パイプライン / Complex pipeline**: 引用が根拠に一致しないと `RetryEvent` を投げて
  **検索からやり直す**循環（lesson 08 の `ModelRetry` のイベント駆動版）。

```
StartEvent ─▶ retrieve ─▶ GenerateEvent ─▶ generate ─▶ VerifyEvent ─▶ verify ─┬▶ StopEvent
                ▲                                                              │
                └──────────────── re_retrieve ◀── RetryEvent ◀────────────────┘
```

## Pydantic AI 版との対比 / Side-by-side with the Pydantic AI version
| 観点 / Aspect | Pydantic AI（lesson 08）| LlamaIndex Workflows（このトラック）|
|---|---|---|
| 制御 / Control | エージェントのツールループ | **イベント駆動の複数ステップ** / event-driven steps |
| 引用検証 / Citation guard | `output_validator` + `ModelRetry` | `verify` ステップ + `RetryEvent` ループ |
| 途中経過 / Progress | 取り出しにくい | `stream_events()` で**ストリーミング** |
| 検索 / Retrieval | キーワード一致（埋め込み非依存）| **同じ**キーワード一致（[`corpus.py`](src/li_rag_workflows/corpus.py)）|

> `CORPUS` と `retrieve` は lesson 08 から移植。`retrieve` を `VectorStoreIndex` に差し替えれば
> 本物のベクトル検索になります（インターフェースは不変）。

## セットアップ / Setup
ルートの uv ワークスペースのメンバーです。リポジトリ直下で同期します。
A member of the root uv workspace — sync from the repo root:

```bash
uv sync
cp .env.example .env   # （任意）実モデルを使うとき / (optional) to use a real model
```

## 実行 / Run
```bash
# オフラインテスト（API キー不要 / no API key — MockLLM を使用）
uv run pytest frameworks/llamaindex-rag-workflows

# 実モデルでデモ（.env 設定後）。進捗イベントが逐次ストリーミング表示される。
uv run python -m li_rag_workflows.workflow
```

## プロバイダ / Providers
既存教材と**同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）を読み、
LlamaIndex の `LLM` を返します（[`provider.py`](src/li_rag_workflows/provider.py)）。
`bootcamp_common` には依存しません。

## 演習 / Exercise
1. `MAX_ATTEMPTS` を増やし、`re_retrieve` の `k`（取得幅）を段階的に広げる戦略を試す。
   Increase `MAX_ATTEMPTS` and widen `k` progressively in `re_retrieve`.
2. `retrieve` を LlamaIndex の `VectorStoreIndex` + 埋め込みに差し替え、本物のベクトル検索にする。
   Swap `retrieve` for a `VectorStoreIndex` with embeddings for real vector search.
3. `generate` で `llm.astream_chat` を使い、モデルの**実トークン**をストリームに流す。
   Stream the model's *real* tokens via `llm.astream_chat` in `generate`.
