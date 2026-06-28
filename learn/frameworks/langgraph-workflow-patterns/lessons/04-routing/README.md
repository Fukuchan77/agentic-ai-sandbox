# L04 — Routing

分類器で仕分け→専門家へ振り分ける **Routing** を、LangGraph の**条件付き辺**で書きます。
**Routing** (classify, then dispatch) via LangGraph **conditional edges** — the track's capstone.

## 学ぶこと / What you'll learn
- `classify` ノードが入力を `billing` / `technical` / `other` に分類する。
- **`add_conditional_edges`** が判定に応じて次ノードを選ぶ（分岐がグラフに刻まれる）。
- 各専門家ノードが応答し、`END` へ。

```
START → classify ─(billing)→  billing  ─→ END
                  ─(technical)→ technical ─→ END
                  ─(other)→    other    ─→ END
```

## コード / Code
[`routing.py`](routing.py) — `build_routing_graph(model=None)` / `run_routing(inquiry)`。

## 実行 / Run
```bash
uv run pytest frameworks/langgraph-workflow-patterns/lessons/04-routing
uv run python -m routing
```

## Pydantic AI 版との対比 / Compare
本体 [Lesson 06](../../../../lessons/06-workflow-patterns/README.md) の `routing`：あちらは `dict[category]`
で引くだけ、こちらは**条件付き辺**で分岐をグラフ化。全体比較は
[`docs/framework-comparison.md`](../../../../../docs/framework-comparison.md)。

## 演習 / Exercise
1. `classify` を `with_structured_output(Route)` 方式に置き換える。
2. 新カテゴリ `sales` をノード＋辺で追加する。
