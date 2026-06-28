# L04 — イベント駆動 RAG / Event-driven RAG

このトラックの集大成。L02（ステップ・イベント）と L03（ストリーミング）を組み合わせ、本体
[Lesson 08](../../../../lessons/08-rag/README.md) の RAG を**イベント駆動の複数ステップ**で書きます。
The track's capstone: combine L02 (steps & events) and L03 (streaming) to rebuild Lesson 08's RAG.

## 学ぶこと / What you'll learn
- **検索 → 生成 → 検証** を別々のステップ（`Event` で結合）に分解する。
- 途中経過と生成トークンを `stream_events()` で**ストリーミング**する。
- 引用が根拠に一致しなければ `RetryEvent` を投げ、**検索からやり直す循環**を作る
  （lesson 08 の `ModelRetry` のイベント駆動版）。

```
StartEvent ─▶ retrieve ─▶ GenerateEvent ─▶ generate ─▶ VerifyEvent ─▶ verify ─┬▶ StopEvent
                ▲                                                              │
                └──────────────── re_retrieve ◀── RetryEvent ◀────────────────┘
```

## コード / Code
[`rag_workflow.py`](rag_workflow.py) — `RagWorkflow` / `ask(question, on_progress=...)`。検索は
共有の [`li_rag_workflows.corpus`](../../src/li_rag_workflows/corpus.py)（キーワード一致・埋め込み非依存）。

## 実行 / Run
```bash
uv run pytest frameworks/llamaindex-rag-workflows/lessons/04-rag
uv run python -m rag_workflow     # 進捗イベントが逐次ストリーミング表示される
```

## Pydantic AI 版との対比 / Compare
| | Pydantic AI（lesson 08）| LlamaIndex Workflows（ここ）|
|---|---|---|
| 引用検証 | `output_validator` + `ModelRetry` | `verify` ステップ + `RetryEvent` ループ |
| 途中経過 | 取り出しにくい | `stream_events()` でストリーミング |

全体比較は [`docs/framework-comparison.md`](../../../../docs/framework-comparison.md)。

## 演習 / Exercise
1. `retrieve` を LlamaIndex の `VectorStoreIndex` + 埋め込みに差し替える。
2. `generate` で `llm.astream_chat` を使い、モデルの**実トークン**を流す。
