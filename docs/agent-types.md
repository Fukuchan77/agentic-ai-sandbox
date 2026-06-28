# エージェントの型と自律性 / Agent Types & Autonomy（Stage 0）

このコースを始める前の **概念オリエンテーション**です。コードは出てきません。
公式（IBM / Anthropic）の整理を、本コースの**どのレッスン／どのパターン**が体現するかに
結びつけて俯瞰します。A concepts-only orientation that maps the official (IBM / Anthropic)
framing onto the lessons and patterns in this course.

> 思想の中核（二軸タクソノミー・Pydantic AI の哲学）は [`concepts.md`](concepts.md)、
> レッスンの順序は [`roadmap.md`](roadmap.md)、全体の学習パスは
> [`learning-path.md`](learning-path.md) を参照。

---

## 1. Generative AI と Agentic AI / Generative vs Agentic AI

IBM「Agentic AI vs. Generative AI」の整理：

| | **Generative AI** | **Agentic AI** |
|---|---|---|
| 起動 / Trigger | 人間のプロンプトに**応答**（呼び出し型）| **目標**を受けて自律的に進める（目標駆動）|
| 行動 / Action | テキスト等を**生成**して終わり | 計画 → **ツールで行動** → 観測 → 再計画 |
| 状態 / State | 基本ステートレス | 文脈・記憶・反復ループを持つ |
| 例 / Example | 要約・翻訳・下書き | 調査して報告書を作る・チケットを解決する |

> Agentic AI は生成 AI を**部品として内包**します。「生成だけ」のステップ（lesson 02 の
> 構造化出力）と、「行動する」ループ（lesson 07 の autonomous loop）の違いを意識すると、
> 以降のパターンが整理して見えます。

---

## 2. AI agent の型 / Types of AI agents

IBM「Types of AI agents」の代表的な分類。実システムは複数の型を**混成（hybrid）**します。

| 型 / Type | 振る舞い / Behavior | 本コースでの接点 / Where it shows up |
|---|---|---|
| **Simple reflex（単純反射）** | 現在の入力だけに条件反応。状態を持たない。 | 1 ショットの単一エージェント（lessons 00–02）|
| **Model-based reflex（モデルベース反射）** | 内部状態で「世界の今」を推定して反応。 | 会話履歴を持つエージェント（lesson 01）|
| **Goal-based（目標ベース）** | 目標から逆算して**行動を選ぶ**。 | Routing / Orchestrator（lesson 06）|
| **Utility-based（効用ベース）** | 複数解を**スコアで比較**して最良を選ぶ。 | Evaluator-Optimizer（lesson 07）, Evals（lesson 11）|
| **Learning（学習）** | 結果から方針を更新する。 | 本コース外（評価→改善のループは lesson 11 が入口）|

> 本コースの**二軸タクソノミー**（[`concepts.md`](concepts.md)）はこの型分類と直交します：
> 「型」は*1 体のエージェントの賢さ*、二軸は*単体 vs オーケストレーション × ワークフロー分類*。

---

## 3. 自律性のレベル / Levels of autonomy

Anthropic「Measuring agent autonomy」は、自律性を**連続的なスペクトラム**として捉えます。
「全自動か否か」ではなく、**どこに人間の判断点を置くか**の設計問題です。

| レベル / Level | 概要 / Summary | 本コース／sandbox での対応 |
|---|---|---|
| **L0 — 単発生成 / single-shot** | 1 回呼んで出力を得る。ループ無し。 | lessons 00–02（構造化出力）|
| **L1 — ツール拡張 / tool-augmented** | ツールを呼ぶが流れは固定。 | lesson 03（tools & deps）, lesson 08（RAG）|
| **L2 — 監督つきループ / supervised loop** | 反復するが**有界**（上限・しきい値・人間確認）。 | lesson 07（`max_iters` ガードレール）, lesson 09（multi-agent）|
| **L3 — 自律ループ / autonomous loop** | エージェントが停止条件まで自分で回す。 | sandbox `patterns/autonomous-agent`, `deep-research`（Stage 4）|

> **自律性が上がるほど、有界性（bounding）と評価（evals）が重要**になります。
> ガードレールは lesson 07、評価は [lesson 11](../learn/lessons/11-evals/README.md)、運用・
> ガバナンスは sandbox の [`governance-and-scale.md`](governance-and-scale.md)
> で扱います（Stage 5）。

---

## 4. 次へ / Next

- 思想を深める → [`concepts.md`](concepts.md)
- 手を動かす → [Lesson 00 — Setup](../learn/lessons/00-setup/README.md)
- 全体像 → [`learning-path.md`](learning-path.md)

## 出典 / Sources
- IBM: [AI agents](https://www.ibm.com/think/topics/ai-agents) ・
  [Types of AI agents](https://www.ibm.com/think/topics/ai-agent-types) ・
  [Agentic AI](https://www.ibm.com/think/topics/agentic-ai) ・
  [Agentic AI vs. Generative AI](https://www.ibm.com/think/topics/agentic-ai-vs-generative-ai)
- Anthropic: [Measuring agent autonomy](https://www.anthropic.com/news/measuring-agent-autonomy) ・
  [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
