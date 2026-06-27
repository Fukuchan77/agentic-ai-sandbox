# LangGraph 版 — ワークフローパターン / Workflow Patterns with LangGraph

[Lesson 06](../../lessons/06-workflow-patterns/README.md) の **Prompt Chaining** と **Routing** を、
Pydantic AI の最小プリミティブではなく **LangGraph の明示的なグラフ構造**（State + nodes + edges）で
書き直した、**完全に独立した**比較トラックです。

A **standalone** comparison track that rewrites Lesson 06's **Prompt Chaining** and
**Routing** using **LangGraph's explicit graph structure** (State + nodes + edges)
instead of Pydantic AI's minimal primitives.

## 学ぶこと / What you'll learn
- **State の設計**: `TypedDict` でグラフ全体の状態を定義し、各ノードが部分更新を返す。
  Design a typed `State`; each node returns a partial update.
- **Chaining = 直列の辺 / serial edges**: `START → outline → write → END`（[`chaining.py`](src/lg_workflow_patterns/chaining.py)）。
- **Routing = 条件付き辺 / conditional edges**: `classify → {billing, technical, other}`（[`routing.py`](src/lg_workflow_patterns/routing.py)）。
- 制御フローが**データ（グラフ）として可視化・検査**できる（`graph.get_graph().draw_mermaid()`）。

## Pydantic AI 版との対比 / Side-by-side with the Pydantic AI version
| 観点 / Aspect | Pydantic AI（lesson 06）| LangGraph（このトラック）|
|---|---|---|
| 制御フロー / Control flow | Python の関数呼び出し / plain function calls | **明示的なグラフ** / explicit graph |
| 状態 / State | 関数の戻り値を手で受け渡し | 共有 `State` を部分更新 / shared state |
| 分岐 / Branching | `dict[category]` で引く | **条件付き辺** / conditional edges |
| 可視化 / Visualization | なし / none | Mermaid 図に出力可 / drawable |

> 題材・カテゴリ（billing / technical / other）は lesson 06 と同一なので 1:1 で比較できます。
> The task and categories match lesson 06 exactly for a 1:1 comparison.

## セットアップ / Setup
このパッケージは**ルートの uv ワークスペースのメンバー**です。リポジトリ直下で一括同期します。
This package is a **member of the root uv workspace**. Sync everything from the repo root:

```bash
# リポジトリ直下で / from the repo root
uv sync
cp .env.example .env   # （任意）実モデルを使うとき / (optional) to use a real model
```

## 実行 / Run
```bash
# オフラインテスト（API キー不要 / no API key — FakeListChatModel を使用）
uv run pytest frameworks/langgraph-workflow-patterns

# 実モデルでデモ（.env 設定後 / after configuring .env）
uv run python -m lg_workflow_patterns.chaining
uv run python -m lg_workflow_patterns.routing
```

## プロバイダ / Providers
既存教材と**同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）を読みます。
返すのは LangChain の chat model です（[`provider.py`](src/lg_workflow_patterns/provider.py)）。
`bootcamp_common` には依存しません。Reads the **same `.env`** as the bootcamp and returns a
LangChain chat model; independent of `bootcamp_common`.

## 演習 / Exercise
1. `classify` を `with_structured_output(Route)` を使う形に変え、テキスト正規化を置き換える。
   Switch `classify` to `with_structured_output(Route)` instead of text normalization.
2. Parallelization をグラフに追加する：`START` から複数ノードへ **fan-out** し、`join` ノードで集約。
   Add Parallelization: fan-out from `START` to several nodes, then aggregate in a `join` node.
