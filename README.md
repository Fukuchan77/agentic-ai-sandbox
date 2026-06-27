# agentic-ai-bootcamp 🤖

**Pydantic AI で Agentic AI / AI agent 開発を、基礎から応用まで一貫して学ぶハンズオン教材。**
**A hands-on bootcamp for building Agentic AI / AI agents with Pydantic AI — from fundamentals to applications.**

- 🧩 **段階的な 11 レッスン / 11 progressive lessons** — 入門 → パターン → 応用（RAG・マルチエージェント・本番化）
- 🛠 **動くコード＋手順 / runnable code + steps** — 各レッスンに例とテストを同梱
- ✅ **API キー不要でテスト / tests need no API key** — `TestModel` / `FunctionModel` で全部オフライン
- 🌐 **日英併記 / bilingual (JP/EN)**
- 🔀 **Anthropic ↔ Ollama 切替 / switchable providers** — `.env` 一行で

> 補足 / Note: この教材は、より高度なリファレンス実装である
> [`pydantic-ai-sandbox`](../README.md) と同じリポジトリ内の独立したサブプロジェクト
> （`bootcamp/`）です。初学者はまずこの bootcamp から始めるのがおすすめです。
> This is a self-contained sub-project (`bootcamp/`) living alongside the more
> advanced reference repo. Beginners should start here.

---

## クイックスタート / Quick start

```bash
# bootcamp/ ディレクトリで / from the bootcamp/ directory
make setup            # 依存をインストール / install deps (uv sync)
cp .env.example .env  # （任意）プロバイダ設定 / (optional) configure a provider
make test             # 全レッスンのオフラインテスト / all offline tests — no API key needed
```

`make test` が緑なら準備完了です。最初のレッスンへ:
If `make test` is green you're ready. Start the first lesson:

👉 [`lessons/00-setup/`](lessons/00-setup/README.md)

実モデルで動かしたい場合は [`docs/provider-setup.md`](docs/provider-setup.md) を参照
（Anthropic か無償の Ollama）。To run against a real model, see the provider setup
(Anthropic, or free local Ollama).

---

## カリキュラム / Curriculum

| # | レッスン / Lesson | 学ぶこと / Focus |
|---|---|---|
| 00 | [Setup](lessons/00-setup/README.md) | 環境構築 + Hello Agent / env + first run |
| 01 | [First Agent](lessons/01-first-agent/README.md) | instructions, sync/async, 会話履歴 |
| 02 | [Structured Output](lessons/02-structured-output/README.md) | `output_type`, 検証リトライ |
| 03 | [Tools & Deps](lessons/03-tools-and-deps/README.md) | ツール, `RunContext`, 依存性注入 |
| 04 | [Testing](lessons/04-testing/README.md) | `TestModel` / `FunctionModel` |
| 05 | [Observability](lessons/05-observability/README.md) | Logfire 計装 |
| 06 | [Workflow Patterns](lessons/06-workflow-patterns/README.md) | Chaining / Routing / Parallelization |
| 07 | [Advanced Agents](lessons/07-advanced-agents/README.md) | Evaluator-Optimizer + ガードレール |
| 08 | [RAG](lessons/08-rag/README.md) | 検索 + 引用検証 |
| 09 | [Multi-Agent](lessons/09-multi-agent/README.md) | 分割→並列調査→統合 |
| 10 | [Production](lessons/10-production/README.md) | FastAPI + SSE ストリーミング |

全体像と前提関係は [`docs/roadmap.md`](docs/roadmap.md)、設計思想は
[`docs/concepts.md`](docs/concepts.md) を参照。
See the roadmap and concepts docs for the big picture and design philosophy.

---

## 🔬 フレームワーク比較トラック / Framework comparison tracks

本体は Pydantic AI ですが、**同じ題材を別フレームワークで書くとどう変わるか**を体験できるよう、
`frameworks/` 以下に**完全に独立したプロジェクト**を並べています。すべて **uv のワークスペース**
（`[tool.uv.workspace]`）で 1 つの venv / 1 つの `uv.lock` に束ねられ、`.env` も共有します。
The bootcamp centers on Pydantic AI, but `frameworks/` holds **fully independent projects**
that rewrite the same tasks in other frameworks, bound together by a **uv workspace**.

| トラック / Track | 書き直す対象 / Rewrites | スタイル / Style |
|---|---|---|
| [`frameworks/langgraph-workflow-patterns`](frameworks/langgraph-workflow-patterns/README.md) | [Lesson 06](lessons/06-workflow-patterns/README.md) Chaining / Routing | **LangGraph のグラフ**（State + nodes + 条件付き辺）|
| [`frameworks/llamaindex-rag-workflows`](frameworks/llamaindex-rag-workflows/README.md) | [Lesson 08](lessons/08-rag/README.md) RAG | **LlamaIndex の Workflows**（イベント駆動・ストリーミング）|

```bash
uv sync                                              # 全メンバーを一括同期 / sync all members
uv run pytest frameworks/langgraph-workflow-patterns # API キー不要 / no API key
uv run pytest frameworks/llamaindex-rag-workflows
```

設計の違いは [`docs/framework-comparison.md`](docs/framework-comparison.md) を参照。
See the framework comparison doc for how the designs differ.

---

## このリポジトリの歩き方 / How to navigate

```
bootcamp/
├── README.md                  # ← いまここ / you are here
├── Makefile                   # setup / test / lint / run の薄いラッパ
├── pyproject.toml             # uv ワークスペース root（pydantic-ai-slim[anthropic,openai]）
├── .env.example               # プロバイダ設定テンプレート（全トラック共通）/ provider config (shared)
├── src/bootcamp_common/
│   └── provider.py            # 全レッスン共通のモデル生成口 / single model factory
├── lessons/NN-*/              # 各レッスン: README + 例(.py) + テスト(test_*.py)
├── frameworks/                # 別フレームワーク版の独立プロジェクト / independent framework tracks
│   ├── langgraph-workflow-patterns/   # lesson 06 を LangGraph で / Chaining & Routing as graphs
│   └── llamaindex-rag-workflows/      # lesson 08 を LlamaIndex Workflows で / event-driven RAG
└── docs/                      # concepts / roadmap / provider-setup / framework-comparison
```

各レッスンフォルダの中身 / Inside each lesson folder:
- `README.md` — 概念と手順（日英）/ concepts & steps (JP/EN)
- `<lesson>.py` — 動く例。`make run FILE=...` で実行 / the runnable example
- `test_<lesson>.py` — オフラインテスト。`make test` で実行 / offline tests

---

## よくある質問 / FAQ

**Q. お金をかけずに全部学べますか？ / Can I learn it all for free?**
A. はい。`make test` は `TestModel`/`FunctionModel` で動くため API キー不要です。実モデルを
試したいときだけ Anthropic キー、または無償の Ollama を使います。
Yes — `make test` needs no key. Use an Anthropic key or free Ollama only to run real calls.

**Q. プロバイダを変えるとコードを書き直しますか？ / Do I rewrite code to switch providers?**
A. いいえ。`.env` の `LLM_PROVIDER` を変えるだけです（`bootcamp_common/provider.py` が吸収）。
No — just change `LLM_PROVIDER` in `.env`.

---

## ライセンス / License
[MIT](LICENSE)
