# LangChain / LangGraph トラック — 基礎から比較まで / from basics to comparison

LangChain のチャットモデルから始め、**LangGraph の明示的なグラフ構造**（State + nodes + edges）を
段階的に学び、最後に本体 [Lesson 06](../../lessons/06-workflow-patterns/README.md) の
**Chaining / Routing** を書き比べる、**完全に独立した**学習トラックです。

A **standalone** learning track: start from the LangChain chat model, build up **LangGraph's
explicit graph structure** step by step, and finish by re-implementing Lesson 06's
**Chaining / Routing** for a side-by-side comparison.

## カリキュラム / Curriculum
| # | レッスン / Lesson | 学ぶこと / Focus | 本体との対応 / Maps to |
|---|---|---|---|
| 01 | [LangChain basics](lessons/01-langchain-basics/README.md) | メッセージ, `invoke`, プロバイダ非依存 | [L01 First Agent](../../lessons/01-first-agent/README.md) |
| 02 | [First graph](lessons/02-first-graph/README.md) | `StateGraph`, State, ノード, 辺（LLM なし）| — |
| 03 | [Chaining](lessons/03-chaining/README.md) | 直列の LLM ノード（出力→入力）| [L06](../../lessons/06-workflow-patterns/README.md) |
| 04 | [Routing](lessons/04-routing/README.md) | **条件付き辺**で分岐 | [L06](../../lessons/06-workflow-patterns/README.md) |

各レッスンに `README.md` + コード + オフラインテストが入っています。共有コードは
[`src/lg_workflow_patterns/`](src/lg_workflow_patterns/)（`provider.py` = chat model 生成、
`chat.py` = メッセージ整形ヘルパ）。

## Pydantic AI 版との対比 / Side-by-side with Pydantic AI
| 観点 / Aspect | Pydantic AI（本体）| LangGraph（このトラック）|
|---|---|---|
| 制御フロー / Control flow | Python の関数呼び出し | **明示的なグラフ** / explicit graph |
| 状態 / State | 関数の戻り値を手で受け渡し | 共有 `State` を部分更新 |
| 分岐 / Branching | `dict[category]` で引く | **条件付き辺** / conditional edges |
| 可視化 / Visualization | なし | Mermaid 図に出力可 / drawable |

## セットアップ / Setup
**ルートの uv ワークスペースのメンバー**です。2 通りの入れ方があります。
A **member of the root uv workspace**. Install it either way:

```bash
# A) このフォルダだけ（LangChain/LangGraph のみ）/ this framework only
cd frameworks/langgraph-workflow-patterns && uv sync

# B) 3 フレームワーク全部（比較学習）/ all three frameworks (for comparison) — repo root
uv sync --all-packages

cp .env.example .env    # （任意）実モデルを使うとき / (optional) to use a real model
```

> 共有 venv は 1 つ。A と B は排他的で、最後に実行した方の状態になります。One shared venv;
> A and B are exclusive — the last one you run wins.

## 実行 / Run
```bash
# トラック全体のオフラインテスト（API キー不要 / no API key）
uv run pytest frameworks/langgraph-workflow-patterns

# レッスン単体（例）/ a single lesson
uv run pytest frameworks/langgraph-workflow-patterns/lessons/04-routing
```
各レッスンの実モデルデモは、そのフォルダの README を参照（`uv run python -m <module>`）。

## プロバイダ / Providers
本体と**同じ `.env`・同じ変数**（`LLM_PROVIDER` で `anthropic` ↔ `ollama`）を読み、LangChain の
chat model を返します（[`provider.py`](src/lg_workflow_patterns/provider.py)）。`bootcamp_common`
には依存しません。全体比較は [`docs/framework-comparison.md`](../../../docs/framework-comparison.md)。
