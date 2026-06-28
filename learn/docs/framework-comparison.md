# フレームワーク比較 / Framework Comparison

この教材の中核は **Pydantic AI** ですが、同じ題材を別フレームワークで書くと設計がどう変わるかを
体験できるよう、`frameworks/` 以下に**完全に独立したトラック**を並べています。すべて **uv の
ワークスペース**で 1 つの venv / 1 つの `uv.lock` に束ねられます。

The bootcamp centers on **Pydantic AI**, but `frameworks/` holds **independent tracks**
that rewrite the same tasks in other frameworks, so you can feel how the design shifts.
A single **uv workspace** binds them into one venv / one `uv.lock`.

---

## インストール / Installation

ワークスペースなので、**目的に応じて入れるものを選べます**（venv は 1 つ・共有）。
Choose what to install depending on your goal (one shared venv):

| 目的 / Goal | 実行場所 / Where | コマンド / Command | 入るもの / Installs |
|---|---|---|---|
| 全部入り（比較学習）| repo root | `uv sync --all-packages` | Pydantic AI + LangChain/LangGraph + LlamaIndex |
| Pydantic AI のみ | repo root | `uv sync` | Pydantic AI |
| LangChain/LangGraph のみ | `frameworks/langgraph-workflow-patterns/` | `uv sync` | LangChain/LangGraph |
| LlamaIndex のみ | `frameworks/llamaindex-rag-workflows/` | `uv sync` | LlamaIndex |

> 各フォルダでの `uv sync` は**排他的**：共有 venv を他フレームワークごと入れ替えます。横断比較は
> root の `--all-packages` を使ってください。Per-folder syncs are exclusive — they swap out the
> other frameworks; use `--all-packages` at the root to compare across frameworks.

### 主要ライブラリのバージョン方針 / Version policy
**メジャーは固定・マイナー/パッチは更新可**（caret 相当の `>=X.Y.Z,<{major+1}`）。正確な版は
`uv.lock` が固定します。Pin the **major**, allow **minor/patch** updates; `uv.lock` pins exact versions.

| ライブラリ / Library | 制約 / Constraint |
|---|---|
| `langchain-core` | `>=1.4.8,<2` |
| `langgraph` | `>=1.2.6,<2` |
| `llama-index-core` | `>=0.14.23,<1` |
| `llama-index-workflows` | `>=2.22.1,<3` |

---

## 比較しながら進める / Compare as you go

1. root で `uv sync --all-packages`。lesson 06 を **Pydantic AI 版**と
   [**LangGraph 版**](../frameworks/langgraph-workflow-patterns/README.md) で動かし、制御フローの
   表現（関数の直列 ↔ 明示グラフ）の違いを見る。
2. lesson 08 を **Pydantic AI 版**と
   [**LlamaIndex Workflows 版**](../frameworks/llamaindex-rag-workflows/README.md) で動かし、
   リトライ（`ModelRetry` ↔ `RetryEvent`）と進捗ストリーミングの違いを見る。
3. 軽くしたいときは各フォルダで `uv sync` し、1 フレームワークだけに絞る。

---

## 3 つのスタイル / Three styles

| | **Pydantic AI**（本体）| **LangGraph** | **LlamaIndex Workflows** |
|---|---|---|---|
| 設計の比喩 / Metaphor | 最小プリミティブの合成 | 明示的な**グラフ** | **イベント駆動**パイプライン |
| 状態 / State | 関数の戻り値 | 共有 `State`（`TypedDict`）| ステップ間を流れる `Event` |
| 分岐 / Branching | `dict` / `if` | **条件付き辺** / conditional edges | イベント型による dispatch |
| ループ / Loops | リトライ例外 (`ModelRetry`) | 辺で循環 / cyclic edges | `Event` 再投入 |
| ストリーミング / Streaming | run の stream API | チャンネル/イベント | `stream_events()` |
| 対応レッスン / Maps to | 全体 / all | [06](../lessons/06-workflow-patterns/) Chaining・Routing | [08](../lessons/08-rag/) RAG |

---

## 各トラックのカリキュラム / Each track is a basics → comparison curriculum

各トラックは `lessons/NN-*/` に**基礎から積み上げる小カリキュラム**を持ち、最後に本体レッスンの
書き直し（到達点）に至ります。各レッスンに README + コード + オフラインテストが付きます。

### `frameworks/langgraph-workflow-patterns/`（LangChain / LangGraph）
1. **01 LangChain basics** — メッセージ・`invoke`・プロバイダ非依存。
2. **02 First graph** — `StateGraph`・State・ノード・辺（LLM なし）。
3. **03 Chaining** — 直列の LLM ノード（`START → outline → write → END`）。
4. **04 Routing** — **条件付き辺**で `classify → {billing, technical, other}`（→ lesson 06 の比較）。

### `frameworks/llamaindex-rag-workflows/`（LlamaIndex）
1. **01 LlamaIndex basics** — `complete`/`acomplete`・プロバイダ非依存。
2. **02 First workflow** — `Workflow`・`@step`・Start/Stop イベント（LLM なし）。
3. **03 Streaming events** — カスタム `Event`・`write_event_to_stream`・`stream_events`。
4. **04 RAG** — `retrieve → generate → verify` + `RetryEvent` 再検索ループ（→ lesson 08 の比較）。

---

## 共通の約束 / Shared conventions

- **同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）。各トラックは自前の
  薄い `provider.py` を持ち、`bootcamp_common` には依存しません（= 完全独立）。
- **API キー不要でテストが緑**。LangGraph は `FakeListChatModel`、LlamaIndex は `ScriptedLLM`
  （[`testing.py`](../frameworks/llamaindex-rag-workflows/src/li_rag_workflows/testing.py)）を注入。
- モデル ID はハードコードせず、すべて `.env` から読みます。

```bash
# リポジトリ直下で全メンバーを同期 / sync every member from the repo root
uv sync --all-packages

# トラックごとのオフラインテスト / per-track offline tests
uv run pytest frameworks/langgraph-workflow-patterns
uv run pytest frameworks/llamaindex-rag-workflows
```
