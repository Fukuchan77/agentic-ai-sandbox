# Lesson 00 — 環境構築と Hello Agent / Setup & Hello Agent

## 学ぶこと / What you'll learn
- uv による環境構築 / Setting up the environment with uv
- `.env` でプロバイダ（Anthropic / Ollama）を切り替える / Switching providers via `.env`
- 最小の `Agent` を 1 つ作って実行する / Building and running one minimal `Agent`
- **API キーなし**でテストする（`TestModel`）/ Testing **without an API key** (`TestModel`)

## 前提モジュール / Prerequisites
なし（ここがスタート）/ None — this is the start.

## 手順 / Steps

```bash
# 1. リポジトリ直下で依存をインストール / install deps from the repo root
make setup            # = uv sync

# 2. 環境変数を用意 / prepare environment variables
cp .env.example .env  # 次に .env を編集 / then edit .env

# 3. オフラインテストを実行（キー不要）/ run offline tests (no key needed)
make test

# 4. （任意）本物のモデルで実行 / (optional) run against a real model
make run FILE=lessons/00-setup/hello_agent.py
```

### `.env` の最小設定 / Minimal `.env`
- **Anthropic を使う場合 / Using Anthropic:**
  `LLM_PROVIDER=anthropic` と `ANTHROPIC_API_KEY=...` を設定。
- **無償で試す場合 / Free, local:**
  `LLM_PROVIDER=ollama` にして、別ターミナルで `ollama serve` と
  `ollama pull llama3.2` を実行。

詳しいセットアップは [`docs/provider-setup.md`](../../../docs/provider-setup.md) を参照。
See [`docs/provider-setup.md`](../../../docs/provider-setup.md) for full setup.

## ポイント解説 / Key points
- `Agent` は Pydantic AI の中心。`model`・`instructions`（システムプロンプト）・
  後で学ぶ `output_type` / `tools` を束ねます。
  `Agent` is the core of Pydantic AI; it bundles a `model`, `instructions`
  (system prompt), and — later — `output_type` / `tools`.
- `build_agent(model=None)` という **ファクトリ形**にしておくと、テストから
  `TestModel` を注入できます。本コース全体でこの形を使います。
  The `build_agent(model=None)` **factory** pattern lets tests inject a
  `TestModel`. We use this pattern throughout the course.

## 演習 / Exercise
1. `instructions` を変えて口調を変えてみる / Change `instructions` to alter the tone.
2. `.env` の `LLM_PROVIDER` を切り替えて、コードを変えずに動くことを確認する。
   Switch `LLM_PROVIDER` in `.env` and confirm the code runs unchanged.
