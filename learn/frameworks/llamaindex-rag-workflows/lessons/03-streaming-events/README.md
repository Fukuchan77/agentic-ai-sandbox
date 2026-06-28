# L03 — イベント & ストリーミング / Events & streaming

カスタムイベントを定義し、ステップの途中経過を**ストリーミング**する方法を学びます。
Define a custom event and **stream** a step's progress to the caller.

## 学ぶこと / What you'll learn
- **カスタム `Event`**: `class TickEvent(Event): msg: str` のように pydantic フィールドで定義。
- **`ctx.write_event_to_stream(...)`**: 最終結果を待たずに途中経過を送る。
- **`handler.stream_events()`**: 呼び出し側が逐次イベントを受け取る（→ UI/SSE）。

```
StartEvent → count → (TickEvent をストリームへ × n) → StopEvent("done")
```

## コード / Code
[`streaming_events.py`](streaming_events.py) — `CountdownWorkflow` / `run_countdown(n, on_tick)`。

## 実行 / Run
```bash
uv run pytest frameworks/llamaindex-rag-workflows/lessons/03-streaming-events
uv run python -m streaming_events     # STREAM> tick 3 / 2 / 1 と表示
```

## ポイント / Key point
次の [L04 RAG](../04-rag/README.md) では、この**ストリーミング**で検索・生成・検証の進捗や生成トークンを
逐次流します。本体 [Lesson 10 Production](../../../../lessons/10-production/README.md) の SSE と発想は同じ。

## 次へ / Next
[L04 — イベント駆動 RAG / event-driven RAG](../04-rag/README.md)
