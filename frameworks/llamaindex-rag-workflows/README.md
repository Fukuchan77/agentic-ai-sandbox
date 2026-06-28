# LlamaIndex トラック — 基礎からイベント駆動 RAG まで / from basics to event-driven RAG

LlamaIndex の LLM 抽象から始め、**イベント駆動の Workflows**（ステップ・イベント・ストリーミング）を
段階的に学び、最後に本体 [Lesson 08](../../lessons/08-rag/README.md) の **RAG** を Workflow で書き比べる、
**完全に独立した**学習トラックです。

A **standalone** learning track: start from the LlamaIndex LLM abstraction, build up **event-driven
Workflows** (steps, events, streaming), and finish by rebuilding Lesson 08's **RAG** as a workflow.

## カリキュラム / Curriculum
| # | レッスン / Lesson | 学ぶこと / Focus | 本体との対応 / Maps to |
|---|---|---|---|
| 01 | [LlamaIndex basics](lessons/01-llamaindex-basics/README.md) | `complete`/`acomplete`, プロバイダ非依存 | [L01 First Agent](../../lessons/01-first-agent/README.md) |
| 02 | [First workflow](lessons/02-first-workflow/README.md) | `Workflow`, `@step`, Start/Stop イベント（LLM なし）| — |
| 03 | [Streaming events](lessons/03-streaming-events/README.md) | カスタム `Event`, `write_event_to_stream`, `stream_events` | [L10 Production](../../lessons/10-production/README.md) |
| 04 | [RAG](lessons/04-rag/README.md) | **イベント駆動 RAG**：検索→生成→検証 + 再検索ループ | [L08 RAG](../../lessons/08-rag/README.md) |

各レッスンに `README.md` + コード + オフラインテストが入っています。共有コードは
[`src/li_rag_workflows/`](src/li_rag_workflows/)（`provider.py` = LLM 生成、`corpus.py` = 知識ベース +
キーワード検索、`testing.py` = オフライン用の決定論 LLM）。

## Pydantic AI 版との対比 / Side-by-side with Pydantic AI
| 観点 / Aspect | Pydantic AI（本体）| LlamaIndex Workflows（このトラック）|
|---|---|---|
| 制御 / Control | エージェントのツールループ | **イベント駆動の複数ステップ** |
| 引用検証 / Citation guard | `output_validator` + `ModelRetry` | `verify` ステップ + `RetryEvent` ループ |
| 途中経過 / Progress | 取り出しにくい | `stream_events()` で**ストリーミング** |

## セットアップ / Setup
**ルートの uv ワークスペースのメンバー**です。2 通りの入れ方があります。
A **member of the root uv workspace**. Install it either way:

```bash
# A) このフォルダだけ（LlamaIndex のみ）/ this framework only
cd frameworks/llamaindex-rag-workflows && uv sync

# B) 3 フレームワーク全部（比較学習）/ all three frameworks (for comparison) — repo root
uv sync --all-packages

cp .env.example .env    # （任意）実モデルを使うとき / (optional) to use a real model
```

> 共有 venv は 1 つ。A と B は排他的で、最後に実行した方の状態になります。One shared venv;
> A and B are exclusive — the last one you run wins.

## 実行 / Run
```bash
# トラック全体のオフラインテスト（API キー不要 / no API key）
uv run pytest frameworks/llamaindex-rag-workflows

# レッスン単体（例）/ a single lesson
uv run pytest frameworks/llamaindex-rag-workflows/lessons/04-rag
```
各レッスンの実モデルデモは、そのフォルダの README を参照（`uv run python -m <module>`）。

## プロバイダ / Providers
本体と**同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）を読み、LlamaIndex の
`LLM` を返します（[`provider.py`](src/li_rag_workflows/provider.py)）。`bootcamp_common` には依存しません。
全体比較は [`docs/framework-comparison.md`](../../docs/framework-comparison.md)。
