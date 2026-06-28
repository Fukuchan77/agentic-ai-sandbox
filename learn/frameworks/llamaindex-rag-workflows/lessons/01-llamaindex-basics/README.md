# L01 — LlamaIndex の基礎 / LlamaIndex basics

LlamaIndex トラックの出発点。Workflows の前に **LLM 抽象**を押さえます。
The starting point — learn the **LLM abstraction** before Workflows.

## 学ぶこと / What you'll learn
- **complete / acomplete**: プロンプトを渡すと `CompletionResponse`。`str(resp)` で本文。
- **プロバイダ非依存 / Provider-agnostic**: `get_llm()` が `.env`（`LLM_PROVIDER`）を見て
  Anthropic か Ollama（OpenAI 互換）の `LLM` を返す。コードは変わらない。
- **async** が基本：Workflows も async なので `acomplete` を使う。

## コード / Code
[`llamaindex_basics.py`](llamaindex_basics.py) — `one_shot(prompt)` が 1 回の補完を返す。

## 実行 / Run
```bash
uv run pytest frameworks/llamaindex-rag-workflows/lessons/01-llamaindex-basics   # オフライン
uv run python -m llamaindex_basics                                               # 実モデル（.env 設定後）
```

## Pydantic AI 版との対応 / Maps to
本体 [Lesson 01 First Agent](../../../../lessons/01-first-agent/README.md) に相当。

## 次へ / Next
[L02 — 最初の Workflow / first workflow](../02-first-workflow/README.md)
