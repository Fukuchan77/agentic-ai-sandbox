# L02 — 最初の Workflow / Your first workflow

LLM はまだ使わず、**Workflow の仕組み**（ステップ・イベント）だけに集中します。
No LLM yet — focus purely on the **workflow mechanics**: steps and events.

## 学ぶこと / What you'll learn
- **`@step`**: async メソッド 1 つが 1 ステップ。**引数のイベント型**で起動条件が決まる。
- **イベントの受け渡し**: ステップは次のイベントを `return` する。
- **StartEvent / StopEvent**: 入口と出口。`StopEvent(result=...)` の結果が `run()` の戻り値。

```
StartEvent → shout → LoudEvent → exclaim → StopEvent   ("hello" → "HELLO" → "HELLO!")
```

## コード / Code
[`first_workflow.py`](first_workflow.py) — `EchoWorkflow` / `run_echo(text)`。

## 実行 / Run
```bash
uv run pytest frameworks/llamaindex-rag-workflows/lessons/02-first-workflow
uv run python -m first_workflow
```

## ポイント / Key point
LangGraph が**辺で経路を宣言**するのに対し、LlamaIndex は**イベント型で結合**します。どのステップが
動くかは「どのイベントが流れたか」で決まる——これがイベント駆動。Where LangGraph declares routes via
edges, LlamaIndex couples steps by **event type** — what runs is decided by what event flows.

## 次へ / Next
[L03 — イベント & ストリーミング / events & streaming](../03-streaming-events/README.md)
