# 統一学習パス / Unified Learning Path — IBM × Anthropic 公式準拠

AI Agents / Agentic AI を **基礎から本番・ガバナンスまで** 一本で学ぶための地図です。
この **モノレポ `agentic-ai-sandbox`** は、**2 つのティア**を **1 つの学習パス**として接続します：

- **[`learn/`](../learn/README.md)** — 学ぶ（Stage 0–3、入口・緩いゲート）
- **[`reference/`](../reference/README.md)** — 参照/本番化・ガバナンス（Stage 4–5・厳格ゲート）

> このページが**唯一の入口**です。レッスン順は [`roadmap.md`](roadmap.md)、設計思想は
> [`concepts.md`](concepts.md)、Stage 0 の概念は [`agent-types.md`](agent-types.md)。
> This page is the single entry point for the whole monorepo (learn/ + reference/ tiers);
> it sits above the roadmap and concepts docs.

---

## 6 ステージの全体像 / The six stages

| Stage | テーマ / Theme | ティア / Tier | 主な入口 / Start here |
|---|---|---|---|
| **0** | 概念オリエンテーション（型・generative vs agentic・自律性）| `learn/` | [`agent-types.md`](agent-types.md), [`concepts.md`](concepts.md) |
| **1** | 基礎 / Foundations（Lessons 00–05）| `learn/` | [Lesson 00](../learn/lessons/00-setup/README.md) |
| **2** | パターン / Patterns（Lessons 06–07 ＋ framework tracks）| `learn/` | [Lesson 06](../learn/lessons/06-workflow-patterns/README.md) |
| **3** | 応用 / Applications（Lessons 08–10 ＋ **11 Evals**）| `learn/` | [Lesson 08](../learn/lessons/08-rag/README.md) |
| **4** | 参照/本番化 / Reference & production | `reference/` | [`patterns/README.md`](../reference/patterns/README.md) |
| **5** | ガバナンス & スケール / Governance & scale | `reference/` | [`governance-and-scale.md`](governance-and-scale.md) |

```
Stage 0  概念 ─ agent-types / concepts          ┐
Stage 1  基礎 ─ Lessons 00–05                    │  learn/（学ぶ / loose gates）
Stage 2  パターン ─ Lessons 06–07 + frameworks   │
Stage 3  応用 ─ Lessons 08–10 + 11 Evals         ┘
            │  ハンドオフ / hand-off（同一リポ内・相対リンク）
            ▼
Stage 4  参照/本番 ─ patterns / contracts / RAG / SSE / deep-research / eval-graders  ┐
Stage 5  ガバナンス ─ identity / scale / deploy / OWASP                                ┘  reference/（厳格ゲート）
```

### 各ステージで身につくこと / What each stage gives you

- **Stage 0 概念** — 用語の地図。型（IBM）・generative vs agentic（IBM）・自律性レベル
  （Anthropic）を、以降のレッスンに結びつけて理解する。
- **Stage 1 基礎** — 単一エージェント：instructions・構造化出力・ツール/DI・テスト・可観測性。
- **Stage 2 パターン** — Anthropic「Building Effective Agents」の合成可能なワークフロー
  （chaining / routing / parallelization / evaluator-optimizer）＋ツール設計。`frameworks/` で
  別フレームワーク版と読み比べ。
- **Stage 3 応用** — RAG・本番配信（SSE/FastAPI）・マルチエージェント・**評価（evals）**。
- **Stage 4 参照/本番** — 同じパターンを 3 フレームワーク横断で、契約・ドリフトテスト・
  カバレッジゲート・SDD・CI 付きの**本番品質**で実装した参照実装。
- **Stage 5 ガバナンス** — identity/権限・エンタープライズ規模での採用・デプロイ・OWASP。

---

## 公式ソース対応表 / Official-source map

各公式ドキュメントが**どの Stage / どのファイル**でカバーされるか。
Which file in this learning path covers each official source.

### IBM
| 公式ソース / Source | Stage | カバー箇所 / Covered by |
|---|---|---|
| [AI agents](https://www.ibm.com/think/topics/ai-agents) | 0 | [`agent-types.md`](agent-types.md), [`concepts.md`](concepts.md) |
| [Agentic AI](https://www.ibm.com/think/topics/agentic-ai) | 0 | [`agent-types.md`](agent-types.md) §1 |
| [Types of AI agents](https://www.ibm.com/think/topics/ai-agent-types) | 0 | [`agent-types.md`](agent-types.md) §2 |
| [Agentic AI vs. Generative AI](https://www.ibm.com/think/topics/agentic-ai-vs-generative-ai) | 0 | [`agent-types.md`](agent-types.md) §1 |
| [Agentic AI architecture patterns](https://www.ibm.com/think/architectures/patterns/agentic-ai) | 2,4 | [Lesson 06](../learn/lessons/06-workflow-patterns/README.md), reference [`patterns/`](../reference/patterns/README.md) |
| [Think: AI agents (hub)](https://www.ibm.com/think/ai-agents) ・ [Insights: agentic AI](https://www.ibm.com/think/insights/agentic-ai) | 0,5 | 概念の出典 / further reading（[`agent-types.md`](agent-types.md), [`governance-and-scale.md`](governance-and-scale.md)）|
| [Agentic AI identity management](https://www.ibm.com/solutions/agentic-ai-identity-management) | 5 | reference [`governance-and-scale.md`](governance-and-scale.md) |
| [Scale agentic AI (IBV report)](https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/scale-agentic-ai) | 5 | reference [`governance-and-scale.md`](governance-and-scale.md) |
| [Deploying agentic AI (watsonx)](https://www.ibm.com/docs/en/watsonx/saas?topic=applications-deploying-agentic-ai) | 3,5 | [Lesson 10](../learn/lessons/10-production/README.md), reference [`governance-and-scale.md`](governance-and-scale.md) |
| [Learning path: Agentic AI in practice](https://www.ibm.com/training/learning-path/agentic-ai-in-practice-1058) | — | 参考カリキュラム / reference curriculum（本パスの設計の比較対象）|

### Anthropic
| 公式ソース / Source | Stage | カバー箇所 / Covered by |
|---|---|---|
| [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) （[resources](https://resources.anthropic.com/building-effective-ai-agents) ・ [更に](https://resources.anthropic.com/ty-building-effective-ai-agents)） | 2,4 | [Lesson 06–07](../learn/lessons/06-workflow-patterns/README.md), reference [`patterns/`](../reference/patterns/README.md) |
| [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 2,4 | 概念=learn [`concepts.md`](concepts.md) §4（＋汎用ツールは [Lesson 03](../learn/lessons/03-tools-and-deps/README.md)）／**動くハンズオン=reference** [`tool_design.py`](../reference/patterns/frameworks/pydantic-ai/src/patterns_pydantic_ai/tool_design.py)・[`docs/tool-design.md`](tool-design.md) |
| [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 3,4 | [Lesson 09](../learn/lessons/09-multi-agent/README.md) で**部分的に**（分割・並列の文脈設計）／**本格ハンズオン=reference** の note-taking・compaction（[`docs/context-engineering.md`](context-engineering.md)、deep-research 本流・Spec 010）|
| [Measuring agent autonomy](https://www.anthropic.com/news/measuring-agent-autonomy) | 0 | [`agent-types.md`](agent-types.md) §3 |
| [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 3,4 | **[Lesson 11](../learn/lessons/11-evals/README.md)**, reference [`patterns/EVAL-GRADERS.md`](../reference/patterns/EVAL-GRADERS.md)（`GradeReport` 横断契約・Spec 011）|
| [Claude solutions: agents](https://claude.com/solutions/agents) | — | 製品事例 / product framing（参考）|
| [Coding agents for social sciences](https://www.anthropic.com/research/coding-agents-social-sciences) ・ [Finance agents](https://www.anthropic.com/news/finance-agents) | — | 業種別の応用例 / vertical case studies（発展）|

> OWASP「Agentic AI / LLM Top 10」は Stage 5 のセキュリティ観点として reference の
> [`patterns/SECURITY-NOTES.md`](../reference/patterns/SECURITY-NOTES.md) と
> [`governance-and-scale.md`](governance-and-scale.md) で扱います。

---

## 進め方 / How to walk the path

1. **Stage 0** を読む（30–60 分）→ [`agent-types.md`](agent-types.md) → [`concepts.md`](concepts.md)。
2. **Stage 1–3** を手で動かす → [`roadmap.md`](roadmap.md) の順に Lessons 00→11。各レッスンは
   `README` → コード → `mise run learn:test`（**API キー不要**）→ 演習。
3. **Stage 4–5** へハンドオフ → [`reference/`](../reference/README.md) の本番品質パターンと、
   Stage 5 の [`governance-and-scale.md`](governance-and-scale.md)（identity / scale / OWASP）へ進む。

```bash
# learn/ ティアから（Stage 1–3、オフライン・API キー不要）
mise run learn:test                       # 全レッスン / all lessons
cd learn && uv run pytest lessons/11-evals -q   # 評価レッスンだけ / just the evals lesson
```
