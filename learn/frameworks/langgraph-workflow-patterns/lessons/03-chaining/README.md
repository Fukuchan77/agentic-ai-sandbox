# L03 — Prompt Chaining

出力を次の入力へ直列に渡す **Prompt Chaining** を、LangGraph の直列グラフで書きます。
**Prompt Chaining** (pipe one step's output into the next) as a serial LangGraph graph.

## 学ぶこと / What you'll learn
- LLM ノードを 2 つ直列に並べ、`State` 経由で出力→入力をつなぐ。
- `outline` ノードの結果を `write` ノードが受け取る（チェーン）。

```
START → outline → write → END
```

## コード / Code
[`chaining.py`](chaining.py) — `build_chaining_graph(model=None)` / `run_chaining(topic)`。
チャット呼び出しは共有ヘルパ [`lg_workflow_patterns.chat.ask`](../../src/lg_workflow_patterns/chat.py) を利用。

## 実行 / Run
```bash
uv run pytest frameworks/langgraph-workflow-patterns/lessons/03-chaining   # FakeListChatModel
uv run python -m chaining                                                  # 実モデル（.env 設定後）
```

## Pydantic AI 版との対比 / Compare
本体 [Lesson 06](../../../../lessons/06-workflow-patterns/README.md) の `prompt_chaining`：あちらは
関数の直接呼び出し、こちらは **State を共有する明示グラフ**。同じ題材で書き比べてください。

## 次へ / Next
[L04 — Routing](../04-routing/README.md)
