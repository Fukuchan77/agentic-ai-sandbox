# Lesson 11 — エージェントの評価 / Evaluating Agents

## 学ぶこと / What you'll learn
- なぜ「テスト」だけでなく「**評価 / evals**」が必要か / why evals, not just tests
- **2 軸**で採点する: **Outcome（成果）** と **Behavior（過程）** / score on two axes
- 各次元 **1–5 + Unknown** と **rationale 必須** / 1–5 ratings + Unknown + required rationale
- **partial credit** での集約（Unknown は除外）/ partial-credit aggregation
- **独立 judge** で self-eval バイアスを避ける / independent judge avoids self-eval bias
- `FunctionModel` で judge を固定し**オフライン**で検証 / pin the judge offline

## 前提モジュール / Prerequisites
[Lesson 04 — Testing](../04-testing/README.md) ・ [Lesson 07 — Advanced Agents](../07-advanced-agents/README.md)

## 手順 / Steps
```bash
uv run pytest lessons/11-evals -q          # オフライン・API キー不要 / offline, no key
uv run python lessons/11-evals/evals.py    # 実モデルで採点 / grade with a real model
```

## ポイント解説 / Key points

### テスト vs 評価 / Tests vs evals
- **テスト**（lesson 04）は決定論的に「壊れていないか」を見る（pass/fail）。
  Tests check "is it broken?" deterministically.
- **評価 / evals** は確率的な出力の**品質**を多軸で採点する。lesson 07 の
  evaluator-optimizer は実行中の収束ゲート（in-the-loop）、本レッスンは**オフライン/CI
  の多軸採点**という別レイヤです。Evals score *quality* of probabilistic output;
  this is the offline/CI layer, distinct from in-loop convergence gates.

### 2 軸グレーダ / The two-axis grader（`GradeReport`）
| 軸 / Axis | 次元 / Dimensions |
|---|---|
| **Outcome（成果）** | `correctness`（正しさ）, `completeness`（網羅）|
| **Behavior（過程）** | `tool_use_discipline`（ツール規律）, `faithfulness`（根拠忠実）|

- 各次元は `1..5`、**証拠が無ければ `None`（Unknown）**。推測で埋めない。
  Each dimension is `1..5`, or `None` (Unknown) — never guess.
- `rationale` は**必須**。なぜその点かを必ず言語化させる。
  A `rationale` is required for every dimension.
- 集約は **partial credit**：既知次元だけ平均（`_axis_mean`）。全 Unknown の軸は
  「採点不能（`None`）」。Aggregation averages only known dimensions.

### 独立 judge / Independent judge
`grade_run(..., judge_model=...)` には**生成に使ったのとは別のモデル**を渡します。
同じモデルに自己採点させると甘くなる（self-eval バイアス）ため。
Pass a model *separate* from the generator; self-grading is biased.

## sandbox への橋渡し / Bridge to the reference repo
本レッスンは**学習用の簡約版**です。本番品質の契約は `pydantic-ai-sandbox` の
**[`patterns/EVAL-GRADERS.md`](../../../reference/patterns/EVAL-GRADERS.md)**（Spec 011・**main にマージ済**）に
正本があり、`patterns/contracts` の**単一ソース**＋ドリフトテストで守られ、evaluator-optimizer /
deep-research / autonomous-agent の **3 パターンで共有**されます。出典は Anthropic「Demystifying
evals for AI agents」。The production-grade contract lives in `pydantic-ai-sandbox`
(`patterns/EVAL-GRADERS.md`, merged to main), shared across three patterns as a single source of truth.

### 本番契約との違い / How the production contract differs
学習用の簡約と本番契約の主な差（本番のほうが厳密）/ key differences:

| 観点 | 本レッスン（教材）| 本番 `GradeReport`（sandbox）|
|---|---|---|
| 軸の持ち方 | 固定 4 次元のフィールド | `outcome_scores: list[AxisScore]` / `behavior_scores: list[AxisScore]`（軸名は自由文字列）|
| rating | `int 1..5` または `None`（Unknown）| `Rating = Literal["1".."5","unknown"]`（**文字列**）|
| rationale | 必須 | **必須かつ非空**（空白のみは構築拒否・loud-fail）|
| 集約 | `overall()` が自前計算 | `aggregate: float`（**ハーネス定義**、NaN/inf 拒否）|
| judge | `judge_model` 注入 | `Judge[SubjectT]` Protocol（注入シーム）＋ `judge_id` 監査メタ |

> 設計思想（outcome/behavior 分離・Unknown・partial credit・独立 judge）は同じです。
> 本番は型をより厳密にし、3 パターン横断の単一契約として固定しています。
> Same ideas; production just hardens the types into one cross-pattern contract.

## 演習 / Exercise
1. `relevance`（関連性）次元を Outcome 軸に追加し、`outcome_score()` が partial credit で
   正しく平均することをテストする。Add a `relevance` dimension and test the average.
2. 全次元が Unknown のとき `overall()` が `0.0` を返すことを確認し、代わりに「採点不能」を
   表す別の戻り値（例外）に変える設計を検討する。Consider returning "unscorable" instead of `0.0`.
3. judge に**わざと甘い**`FunctionModel` を渡し、独立 judge の重要性をテストで示す。
   Show why an independent judge matters with a deliberately lenient `FunctionModel`.
