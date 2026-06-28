# 学習ロードマップ / Learning Roadmap

基礎 → 応用へ、段階的に難度が上がります。上から順に進めるのが推奨です。
Difficulty ramps from foundations to applications. Going top-to-bottom is recommended.

> このロードマップはモノレポ（`learn/` + `reference/`）を貫く [`learning-path.md`](learning-path.md) の **Stage 1–3** に当たります。
> 概念（Stage 0）は [`agent-types.md`](agent-types.md)、本番/ガバナンス（Stage 4–5）は [`reference/`](../reference/README.md) へ。
> This roadmap is Stages 1–3 of the monorepo-wide [`learning-path.md`](learning-path.md).

```
概念 / Concepts（Stage 0 — コード無し / no code）
  ▶ agent-types.md ..... 型 / generative vs agentic / 自律性レベル
  ▶ concepts.md ........ 二軸タクソノミー・設計思想 / taxonomy & philosophy
        │
        ▼
基礎 / Foundations
  00 Setup .............. 環境構築 + Hello Agent / env + first run
  01 First Agent ........ instructions, sync/async, 会話履歴 / conversation
  02 Structured Output .. output_type, 検証リトライ / validation retry
  03 Tools & Deps ....... ツール, RunContext, 依存性注入 / DI
  04 Testing ............ TestModel / FunctionModel（API キー不要 / no key）
  05 Observability ...... Logfire 計装 / instrumentation
        │
        ▼
パターン / Patterns
  06 Workflow Patterns .. Prompt Chaining / Routing / Parallelization  🔬 LangGraph 版あり
  07 Advanced Agents .... Evaluator-Optimizer + ガードレール / guardrails
        │
        ▼
応用 / Applications
  08 RAG ................ 検索 + 引用検証 / retrieval + grounded citations  🔬 LlamaIndex Workflows 版あり
  09 Multi-Agent ........ 分割→並列調査→統合 / decompose → parallel → synthesize
  10 Production ......... FastAPI + SSE ストリーミング / serving & streaming
  11 Evals ............. outcome+behavior の 2 軸採点 / two-axis grading
        │
        ▼
参照/本番・ガバナンス / Reference & governance（Stage 4–5 — reference/ へ）
  ▶ reference/ ………… 3 フレームワーク横断の本番品質実装 + identity/scale/OWASP
```

> 🔬 印のレッスンは別フレームワーク版があり、同じ題材を比較できます（lesson 06 → LangGraph、
> lesson 08 → LlamaIndex Workflows）。詳細は [`framework-comparison.md`](framework-comparison.md)。
> Lessons marked 🔬 have a parallel implementation in another framework for comparison.

## モジュール依存関係 / Module dependencies

| Lesson | 前提 / Requires |
|---|---|
| 00 Setup | — |
| 01 First Agent | 00 |
| 02 Structured Output | 01 |
| 03 Tools & Deps | 02 |
| 04 Testing | 03 |
| 05 Observability | 04 |
| 06 Workflow Patterns | 01–05（基礎修了 / foundations）|
| 07 Advanced Agents | 06 |
| 08 RAG | 02, 03 |
| 09 Multi-Agent | 06, 07 |
| 10 Production | 01 + 基礎全般 / foundations |
| 11 Evals | 04, 07 |

## 進め方 / How to work through it

各レッスンのフォルダで:
1. `README.md` を読む（概念）/ read the README (concepts).
2. コードを読む / read the `*.py` example.
3. `mise run learn:test` で**オフライン**に挙動を確認 / verify behavior offline.
4. 余裕があれば実モデルで実行 / optionally run against a real model.
5. 末尾の**演習**に挑戦 / try the exercises.

```bash
mise run learn:test                              # 全レッスンのテスト / all lesson tests
cd learn && uv run pytest lessons/03-tools-and-deps -q   # 単一レッスンだけ / a single lesson
mise run learn:run -- lessons/01-first-agent/first_agent.py
```
