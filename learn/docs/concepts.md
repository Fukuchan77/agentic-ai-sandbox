# コンセプト / Concepts — Agentic AI と AI Agent

このコースを貫く考え方を、最初に俯瞰しておきましょう。
A bird's-eye view of the ideas that run through the whole course.

> **先に読むと良い / Read first:** エージェントの**型**（IBM）・**Generative vs Agentic**・
> **自律性レベル**（Anthropic）の整理は [`agent-types.md`](agent-types.md)（Stage 0）にまとめています。
> 本ページはその上で、コースを貫く**設計思想**（二軸タクソノミー等）を扱います。
> See [`agent-types.md`](agent-types.md) for agent *types* and *autonomy levels*; this page covers the
> design philosophy on top of that.

---

## 1. AI Agent と Agentic AI / AI Agent vs Agentic AI

| 用語 / Term | 粒度 / Granularity | このコースでの例 / Example here |
|---|---|---|
| **AI Agent** | 単一の構成要素。1 つのモデル＋（任意の）ツール＋構造化出力で 1 タスクをこなす。 A single building block: one model + tools + typed output doing one task. | Lessons 00–05, 08 |
| **Agentic AI** | 複数エージェントの**オーケストレーション**。分解・並列・評価・統合で大きな問題を解く。 Orchestration of *several* agents: decompose, parallelize, evaluate, synthesize. | Lessons 06, 07, 09 |

> 粒度区分は IBM の整理に倣っています。単一エージェントを十分に理解してから、複数の協調へ
> 進むのが本コースの順序です。Granularity framing follows IBM. We master single agents
> first, then move to multi-agent coordination.

---

## 2. 二軸タクソノミー / A two-axis taxonomy

エージェントの「型」は 2 つの直交する軸で整理すると見通しが良くなります。
Agent designs are clearest along two orthogonal axes.

**縦軸 / Vertical — Anthropic「Building Effective Agents」のワークフロー分類:**
- Prompt Chaining（直列）/ Routing（仕分け）/ Parallelization（並列）
- Orchestrator-Workers（動的計画→並列）/ Evaluator-Optimizer（生成⇄評価）
- Autonomous Agent（ツールループ＋停止条件）

**横軸 / Horizontal — IBM の粒度:** AI Agent ↔ Agentic AI

> Anthropic の中核主張 / The core claim:
> *"the most successful implementations weren't using complex frameworks ... they
> were building with simple, composable patterns."*
> 本コースもこの方針で、最小プリミティブからパターンを組み立てます。

**応用レイヤ / Application layers**（ワークフロー分類とは別軸 / orthogonal to the above）:
- **RAG**（lesson 08）— 外部知識の注入 / inject external knowledge
- **Multi-Agent / Deep Research**（lesson 09）— 既存パターンの合成 / composition of patterns
- **配信・本番化**（lesson 10）— SSE ストリーミング, FastAPI / serving & SSE

---

## 3. Pydantic AI の設計思想 / The Pydantic AI philosophy

1. **型を中心に / Types first** — `output_type` に Pydantic モデルを渡し、検証済みの
   オブジェクトを得る。検証失敗は自動リトライ（lesson 02）。
2. **依存性注入 / Dependency injection** — ツールは `RunContext` 経由で deps にアクセス。
   本番は実クライアント、テストはフェイク（lesson 03）。
3. **オフラインでテスト可能 / Testable offline** — `TestModel` / `FunctionModel` で
   API キーなしに全挙動を固定（lesson 04）。
4. **可観測性は一級市民 / Observability is first-class** — `instrument_pydantic_ai()` で
   OpenTelemetry スパンを自動発行（lesson 05）。
5. **モデル非依存 / Provider-agnostic** — `Model` 抽象でプロバイダを差し替え。本コースは
   `LLM_PROVIDER` 一つで Anthropic ↔ Ollama を切替（`bootcamp_common/provider.py`）。

---

## 4. ツール設計のベストプラクティス / Tool-design best practices

Anthropic「Writing tools for agents」より、実務で効く原則:

- **命名と名前空間 / Naming & namespacing** — `get_temperature` のように動詞＋対象で明確に。
  関連ツールは接頭辞で束ねる（`kb_search`, `kb_get`）。
- **トークン効率 / Token efficiency** — 大きな結果はページング・フィルタ・truncation を
  ツール側で行い、文脈を汚さない。
- **最小権限 / Least privilege** — エージェントに渡すツールは必要最小限に。危険な操作は
  ガードレール（lesson 07）と人間の確認の背後に置く。
- **明確な返り値 / Clear returns** — ツールの戻り値はモデルが解釈しやすい簡潔な文字列／
  構造にする。失敗は「何が起きたか」を含める（lesson 03 の "データがありません"）。

---

## 5. ガードレールと安全 / Guardrails & safety

自律性が上がるほど、**有界性**が重要になります。
The more autonomy, the more bounding matters.

- 反復上限（`max_iters`）・使用量上限（`UsageLimits`）・タイムアウト（lesson 07）
- 引用検証で根拠のない出力を弾く（`output_validator` + `ModelRetry`, lesson 08）
- 本番では認証・レート制限・監査ログ（lesson 10）

> 参考 / See also: OWASP「Agentic AI / LLM Top 10」、Anthropic / IBM / Google の
> Agentic AI ガイド。
