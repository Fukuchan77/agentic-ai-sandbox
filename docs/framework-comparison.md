# フレームワーク比較 / Framework Comparison

この教材の中核は **Pydantic AI** ですが、同じ題材を別フレームワークで書くと設計がどう変わるかを
体験できるよう、`frameworks/` 以下に**完全に独立したトラック**を並べています。すべて **uv の
ワークスペース**で 1 つの venv / 1 つの `uv.lock` に束ねられます。

The bootcamp centers on **Pydantic AI**, but `frameworks/` holds **independent tracks**
that rewrite the same tasks in other frameworks, so you can feel how the design shifts.
A single **uv workspace** binds them into one venv / one `uv.lock`.

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

## どのトラックが何を書き直したか / What each track rewrites

### `frameworks/langgraph-workflow-patterns/` — lesson 06
- **Prompt Chaining** → `START → outline → write → END` の直列グラフ。
- **Routing** → `classify → {billing, technical, other}` を**条件付き辺**で分岐。
- 題材・カテゴリは lesson 06 と同一。制御フローが**グラフ（データ）として可視化**できるのが要点。

### `frameworks/llamaindex-rag-workflows/` — lesson 08
- **RAG** を `retrieve → generate → verify` の**イベント駆動ステップ**で表現。
- 途中経過を `stream_events()` で**ストリーミング**、引用検証の失敗は `RetryEvent` で
  **検索からやり直す循環**（lesson 08 の `ModelRetry` のイベント駆動版）。
- 検索は lesson 08 と同じキーワード一致（埋め込み非依存）。

---

## 共通の約束 / Shared conventions

- **同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）。各トラックは自前の
  薄い `provider.py` を持ち、`bootcamp_common` には依存しません（= 完全独立）。
- **API キー不要でテストが緑**。LangGraph は `FakeListChatModel`、LlamaIndex は `MockLLM` を注入。
- モデル ID はハードコードせず、すべて `.env` から読みます。

```bash
# リポジトリ直下で一括同期 / sync everything from the repo root
uv sync

# トラックごとのオフラインテスト / per-track offline tests
uv run pytest frameworks/langgraph-workflow-patterns
uv run pytest frameworks/llamaindex-rag-workflows
```
