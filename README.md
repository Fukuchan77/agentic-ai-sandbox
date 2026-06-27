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
uv sync --all-packages            # 3 フレームワーク全部を導入 / install all three frameworks
cp .env.example .env              # （任意）プロバイダ設定 / (optional) configure a provider
uv run pytest                     # 全レッスンのオフラインテスト / all offline tests — no API key needed
```

`uv run pytest` が緑なら準備完了です。最初のレッスンへ:
If tests are green you're ready. Start the first lesson:

👉 [`lessons/00-setup/`](lessons/00-setup/README.md)

### インストールの選び方 / Choosing what to install

uv ワークスペースなので、**何を入れるか**を目的に応じて選べます（venv は 1 つ・共有）。
A uv workspace lets you install exactly what you need (one shared venv):

| 目的 / Goal | 実行場所 / Where | コマンド / Command | 入るもの / Installs |
|---|---|---|---|
| 比較しながら学ぶ（推奨）| repo root | `uv sync --all-packages` | Pydantic AI + LangChain/LangGraph + LlamaIndex |
| Pydantic AI のみ | repo root | `uv sync` | Pydantic AI |
| LangChain/LangGraph のみ | `frameworks/langgraph-workflow-patterns/` | `uv sync` | LangChain/LangGraph |
| LlamaIndex のみ | `frameworks/llamaindex-rag-workflows/` | `uv sync` | LlamaIndex |

> 各フォルダでの `uv sync` は**排他的**（共有 venv を他フレームワークごと入れ替え）。横断比較は
> root の `--all-packages` を使ってください。Per-folder syncs are exclusive; use `--all-packages`
> at the root for cross-framework comparison.

実モデルで動かしたい場合は [`docs/provider-setup.md`](docs/provider-setup.md) を参照
（Anthropic か無償の Ollama）。To run against a real model, see the provider setup
(Anthropic, or free local Ollama).

---

## カリキュラム / Curriculum

各レッスンは Pydantic AI で学びます。**🔬 列**が付いたレッスンには別フレームワーク版があり、
**同じ題材を読み比べ**られます。Each lesson is taught in Pydantic AI; rows marked **🔬** have a
parallel implementation in another framework so you can **compare the same task side by side**.

| # | レッスン / Lesson | 学ぶこと / Focus | 🔬 別フレームワーク版 / Compare |
|---|---|---|---|
| 00 | [Setup](lessons/00-setup/README.md) | 環境構築 + Hello Agent / env + first run | — |
| 01 | [First Agent](lessons/01-first-agent/README.md) | instructions, sync/async, 会話履歴 | — |
| 02 | [Structured Output](lessons/02-structured-output/README.md) | `output_type`, 検証リトライ | — |
| 03 | [Tools & Deps](lessons/03-tools-and-deps/README.md) | ツール, `RunContext`, 依存性注入 | — |
| 04 | [Testing](lessons/04-testing/README.md) | `TestModel` / `FunctionModel` | — |
| 05 | [Observability](lessons/05-observability/README.md) | Logfire 計装 | — |
| 06 | [Workflow Patterns](lessons/06-workflow-patterns/README.md) | Chaining / Routing / Parallelization | 🔬 [LangGraph 版](frameworks/langgraph-workflow-patterns/README.md) |
| 07 | [Advanced Agents](lessons/07-advanced-agents/README.md) | Evaluator-Optimizer + ガードレール | — |
| 08 | [RAG](lessons/08-rag/README.md) | 検索 + 引用検証 | 🔬 [LlamaIndex Workflows 版](frameworks/llamaindex-rag-workflows/README.md) |
| 09 | [Multi-Agent](lessons/09-multi-agent/README.md) | 分割→並列調査→統合 | — |
| 10 | [Production](lessons/10-production/README.md) | FastAPI + SSE ストリーミング | — |
| 11 | [Evals](lessons/11-evals/README.md) | outcome+behavior の 2 軸採点 / two-axis grading | — |

2 リポを貫く全体の地図は [`docs/learning-path.md`](docs/learning-path.md)（**ここが入口**）。
全体像と前提関係は [`docs/roadmap.md`](docs/roadmap.md)、概念（型・自律性）は
[`docs/agent-types.md`](docs/agent-types.md)、設計思想は [`docs/concepts.md`](docs/concepts.md)、
フレームワーク比較は [`docs/framework-comparison.md`](docs/framework-comparison.md) を参照。
Start with the cross-repo [`docs/learning-path.md`](docs/learning-path.md); see roadmap, agent-types,
concepts, and framework-comparison for the rest.

---

## 🔬 フレームワーク比較トラック / Framework comparison tracks

本体は Pydantic AI ですが、**各フレームワークを基礎から学び、同じ題材を書き比べられる**よう、
`frameworks/` 以下に**完全に独立したプロジェクト**を並べています。各トラックは
**基礎 → 比較**の小カリキュラム（`lessons/NN-*/`）になっています。すべて **uv のワークスペース**
（`[tool.uv.workspace]`）で 1 つの venv / 1 つの `uv.lock` に束ねられ、`.env` も共有します。
The bootcamp centers on Pydantic AI, but `frameworks/` holds **fully independent projects** — each a
small **basics → comparison** curriculum — bound together by a **uv workspace**.

| トラック / Track | カリキュラム / Curriculum | 到達点（本体との比較）/ Capstone |
|---|---|---|
| [`frameworks/langgraph-workflow-patterns`](frameworks/langgraph-workflow-patterns/README.md) | LangChain 基礎 → 最初のグラフ → Chaining → Routing | [Lesson 06](lessons/06-workflow-patterns/README.md) を **LangGraph のグラフ**で |
| [`frameworks/llamaindex-rag-workflows`](frameworks/llamaindex-rag-workflows/README.md) | LlamaIndex 基礎 → 最初の Workflow → ストリーミング → RAG | [Lesson 08](lessons/08-rag/README.md) を **イベント駆動 Workflows**で |

```bash
uv sync --all-packages                               # 全メンバーを一括同期 / sync all members
uv run pytest frameworks/langgraph-workflow-patterns # API キー不要 / no API key
uv run pytest frameworks/llamaindex-rag-workflows
```

設計の違い・比較しながら進める手順は [`docs/framework-comparison.md`](docs/framework-comparison.md) を参照。
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

## 次の一歩 / Next step — pydantic-ai-sandbox（Stage 4–5）

この bootcamp（Stage 0–3）を終えたら、**参照/本番化・ガバナンス**へ進みます。
[`pydantic-ai-sandbox`](../pydantic-ai-sandbox/README.md) は同じパターンを **3 フレームワーク
横断**で、契約・ドリフトテスト・カバレッジゲート・SDD・CI 付きの**本番品質**で実装した参照
リポジトリです（Stage 4）。さらに identity 管理・エンタープライズ規模・OWASP を扱う
[`governance-and-scale.md`](../pydantic-ai-sandbox/docs/governance-and-scale.md)（Stage 5）へ。
After Stages 0–3 here, hand off to the reference/production repo for Stages 4–5.

全体の地図は [`docs/learning-path.md`](docs/learning-path.md)。See the unified learning path.

---

## ライセンス / License
[MIT](LICENSE)
