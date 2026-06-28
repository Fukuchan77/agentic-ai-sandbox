# Stage 5 — ガバナンス & スケール / Governance & Scale

> **このページは Stage 5 の正本です。** 学習パスの最終段で、エージェントを **試作から本番・組織規模**へ
> 引き上げるときの「アイデンティティ／スケール／デプロイ／セキュリティ」を、IBM・Anthropic・OWASP の
> ガイダンスと、本リポジトリの **動く実装**（`reference/`）に橋渡しして整理します。
> **This is the canonical Stage 5 page.** It maps the IBM / Anthropic / OWASP guidance for taking
> agents _from prototype to production at organisational scale_ onto this repo's working implementations
> under `reference/`.

- 前段 / Comes after: Stage 4（[`reference/`](../reference/README.md) の参照実装・パターン）。
- 全体地図 / Map: [`learning-path.md`](learning-path.md) ／ 概念は [`agent-types.md`](agent-types.md)・[`concepts.md`](concepts.md)。
- 実装の深掘り / Deep dive: [`reference/patterns/SECURITY-NOTES.md`](../reference/patterns/SECURITY-NOTES.md)（CVE 根拠＋OWASP マッピングの正本）。

---

## 0. なぜ Stage 5 か / Why a governance stage

Stage 0–4 で「動くエージェント」を作れるようになります。本番ではそこに **3 つの非機能要件**が乗ります：

1. **誰が・何の権限で動くのか（Identity）** — エージェントは人間に代わって行動するため、認証・認可・監査が
   人間ユーザーと同等以上に必要。
2. **試作が組織規模で壊れないか（Scale）** — 1 体のデモから、多数・常時稼働・相互運用へ。
3. **逸脱・悪用をどう抑えるか（Security / Governance）** — 自律性が上がるほど、有界化（bounding）と
   評価（evals）の重みが増す（[`agent-types.md`](agent-types.md) の自律性レベル参照）。

> 自律性とリスクは比例します。ガードレールは [Lesson 07](../learn/lessons/07-advanced-agents/README.md)、
> 評価は [Lesson 11](../learn/lessons/11-evals/README.md) と
> [`reference/patterns/EVAL-GRADERS.md`](../reference/patterns/EVAL-GRADERS.md) が下支えです。
> Autonomy scales with risk; guardrails (Lesson 07) and evals (Lesson 11 / EVAL-GRADERS) are the backstop.

---

## 1. アイデンティティ & アクセス / Identity & access

エージェントは **非人間アイデンティティ（NHI）** として扱います。鍵は「最小権限・短命クレデンシャル・
監査可能性」。本リポジトリでは provider 資格情報の取り回しがその縮図です。

| 原則 / Principle                | 本番での要求 / Production requirement | このリポでの対応 / In this repo                                                                                                    |
| ------------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 最小権限 / Least privilege      | エージェントの権限はタスク境界に限定  | ツール設計で副作用を絞る（[`tool-design.md`](tool-design.md)）                                                                     |
| 短命・非ハードコード credential | 鍵は環境注入・ローテーション前提      | `.env` ＋ `LLM_PROVIDER` 切替、`forbid-hardcoded-model-ids` ゲート（pre-commit / [`reference/README.md`](../reference/README.md)） |
| 秘密の非漏洩                    | ログ・トレースに鍵を残さない          | gitleaks（`.gitleaks.toml`）＋ Logfire 計装の scrubbing                                                                            |
| 監査可能性 / Auditability       | 「誰が・いつ・何を」を追える          | OpenTelemetry / Logfire によるトレース（各レーンの `configure_tracing`）                                                           |

- 出典 / Source: IBM **Agentic AI identity management** — <https://www.ibm.com/solutions/agentic-ai-identity-management>

---

## 2. スケール / Scale — from pilot to production

「動いた」から「組織で回す」への移行は、技術より **運用境界の設計**が支配的です。

- **独立したレーン境界**：本リポの `reference/patterns/` は各パターンを独立 uv プロジェクトに分離し、
  lockfile・カバレッジ・契約ドリフト検知をレーンごとに持ちます。1 つの変更が全体を揺らさない
  「ブラスト半径の最小化」がスケールの前提（[`reference/patterns/README.md`](../reference/patterns/README.md)）。
- **契約の単一正本**：`patterns/contracts` が I/O モデルの単一ソースで、README＝実装のドリフトを CI で検知。
  多数のエージェント／チームが同じ契約を共有しても腐らせない仕組み。
- **観測性をデフォルトに**：全レーンが OTLP エクスポータ前提のトレースを持ち、本番でのデバッグ・容量計画・
  異常検知の土台になる。
- **コスト/レイテンシの有界化**：マルチエージェントは並列度・深さ・トークンを明示的に上限化する
  （[`context-engineering.md`](context-engineering.md) と deep-research 本流）。

- 出典 / Sources:
  - IBM IBV **Scale agentic AI** — <https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/scale-agentic-ai>
  - IBM Think hub — <https://www.ibm.com/think/ai-agents> ／ Insights — <https://www.ibm.com/think/insights/agentic-ai>

---

## 3. デプロイ & 運用 / Deploy & operate

本リポの `reference/app/`（FastAPI プラットフォーム）が、デプロイ可能なエージェント面の最小実体です。

- **プロバイダ非依存のデプロイ**：Anthropic / Ollama / watsonx を `LLM_PROVIDER` で切替（SDK / LiteLLM 経路）。
  本番は managed（watsonx 等）、ローカル/CI はオフライン fake で同一コードを回す。
- **段階的ロールアウト**：オフライン unit（API キー不要）→ ゲート付き live integration（Ollama/watsonx）を
  CI の path フィルタで分離（`reference-ci` / `integration-*` ワークフロー）。
- **本番化レッスンとの接続**：[Lesson 10](../learn/lessons/10-production/README.md)（FastAPI + SSE）が学習側の入口、
  `reference/app/` がその本番品質版。

- 出典 / Source: IBM watsonx **Deploying agentic AI** — <https://www.ibm.com/docs/en/watsonx/saas?topic=applications-deploying-agentic-ai>

---

## 4. セキュリティ & OWASP / Security & OWASP Agentic Top 10

Stage 5 の安全性の **正本は実装側**にあります。プロバイダ非依存のガードレールと、応用レイヤ
（autonomous-agent / RAG / SSE / deep-research）ごとの **OWASP Agentic AI Top 10 / LLM Top 10 マッピング**は
[`reference/patterns/SECURITY-NOTES.md`](../reference/patterns/SECURITY-NOTES.md) に集約しています。

| 関心事 / Concern                   | 正本 / Canonical source                                                                                                                             |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| CVE 根拠・依存フロア               | [`SECURITY-NOTES.md` §CVE 根拠と依存フロア](../reference/patterns/SECURITY-NOTES.md)                                                                |
| OWASP Agentic Top 10 マッピング    | [`SECURITY-NOTES.md` §OWASP](../reference/patterns/SECURITY-NOTES.md) ＋ [`autonomous-agent`](../reference/patterns/autonomous-agent/README.md)     |
| RAG / SSE / Deep Research の脅威面 | [`SECURITY-NOTES.md`](../reference/patterns/SECURITY-NOTES.md) の各応用レイヤ節 ＋ [`deep-research`](../reference/patterns/deep-research/README.md) |
| 評価による逸脱検知                 | [Lesson 11](../learn/lessons/11-evals/README.md), [`EVAL-GRADERS.md`](../reference/patterns/EVAL-GRADERS.md)                                        |

- 出典 / Source: **OWASP GenAI Security Project**（Agentic AI Top 10 / LLM Top 10）— <https://genai.owasp.org/>
- Anthropic: **Building effective agents**（有界なワークフロー設計）— <https://www.anthropic.com/engineering/building-effective-agents>

---

## まとめ / Summary

| 軸 / Axis | 問い / Question          | このリポの答え / This repo's answer                                                       |
| --------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| Identity  | 誰の権限で動くか         | 最小権限ツール＋非ハードコード credential＋トレース                                       |
| Scale     | 組織規模で壊れないか     | 独立レーン境界＋契約単一正本＋観測性デフォルト                                            |
| Deploy    | どう本番に出すか         | provider 非依存 `reference/app/`＋path フィルタ CI                                        |
| Security  | 逸脱・悪用をどう抑えるか | [`SECURITY-NOTES.md`](../reference/patterns/SECURITY-NOTES.md) の OWASP マッピング＋evals |

← 戻る / Back: [`learning-path.md`](learning-path.md)（Stage 0–5 の地図）
