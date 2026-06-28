# L02 — 最初のグラフ / Your first graph

LLM はまだ使わず、**グラフの仕組み**（State・ノード・辺）だけに集中します。
No LLM yet — focus purely on the **graph mechanics**: State, nodes, edges.

## 学ぶこと / What you'll learn
- **State**: `TypedDict` でグラフ全体の状態を定義する。
- **ノード / Nodes**: State を読み、**更新分の dict** を返す純粋な関数。
- **辺 / Edges**: `START → shout → exclaim → END` を `add_edge` でつなぐ。
- **compile → invoke**: グラフを実行し、最終 State を得る。
- **可視化 / Visualization**: `graph.get_graph().draw_mermaid()` で構造を図示できる。

```
START → shout → exclaim → END     ("hello" → "HELLO" → "HELLO!")
```

## コード / Code
[`first_graph.py`](first_graph.py) — `build_first_graph()` / `run_first(text)`。

## 実行 / Run
```bash
uv run pytest frameworks/langgraph-workflow-patterns/lessons/02-first-graph
uv run python -m first_graph     # 結果 + Mermaid 図を表示 / prints result + Mermaid
```

## ポイント / Key point
Pydantic AI では制御フローは Python のコードでしたが、LangGraph では**グラフ＝データ**。
だから可視化・検査・分岐の追加が容易になります。In LangGraph the control flow *is* data,
so it can be drawn, inspected, and extended.

## 次へ / Next
[L03 — Prompt Chaining](../03-chaining/README.md)（ここで初めて LLM ノードを使う）
