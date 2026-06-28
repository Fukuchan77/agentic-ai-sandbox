# L01 — LangChain の基礎 / LangChain basics

LangGraph トラックの出発点。グラフの前に **LangChain のチャットモデル**を押さえます。
The starting point of the LangGraph track — learn the **LangChain chat model** before graphs.

## 学ぶこと / What you'll learn
- **メッセージ / Messages**: 会話は `SystemMessage` / `HumanMessage` の列で表す。
- **invoke**: メッセージ列を渡すと `AIMessage` が返る。`.content` を文字列に正規化する。
- **プロバイダ非依存 / Provider-agnostic**: `get_chat_model()` が `.env`（`LLM_PROVIDER`）を見て
  Anthropic か Ollama の `BaseChatModel` を返す。コードは変わらない。

## コード / Code
[`langchain_basics.py`](langchain_basics.py) — `one_shot(system, user)` が 1 ターンの応答を返す。

## 実行 / Run
```bash
uv run pytest frameworks/langgraph-workflow-patterns/lessons/01-langchain-basics   # オフライン
uv run python -m langchain_basics                                                  # 実モデル（.env 設定後）
```

## Pydantic AI 版との対応 / Maps to
本体 [Lesson 01 First Agent](../../../../lessons/01-first-agent/README.md) に相当（同じ「最初の 1 回」を
LangChain のメッセージ + `invoke` で書いたもの）。

## 次へ / Next
[L02 — 最初のグラフ / first graph](../02-first-graph/README.md)
