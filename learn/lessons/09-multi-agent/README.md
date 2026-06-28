# Lesson 09 — マルチエージェント / Multi-Agent (Deep Research)

## 学ぶこと / What you'll learn
- 「分割 → 並列調査 → 統合」のオーケストレーション / decompose → parallel → synthesize
- `asyncio.Semaphore` による**有界並列** / bounded parallelism with a semaphore
- 役割ごとにエージェントを分け、別々にテストする / role-split agents, tested separately

## 前提モジュール / Prerequisites
[Lesson 06](../06-workflow-patterns/README.md), [Lesson 07](../07-advanced-agents/README.md)

## 手順 / Steps
```bash
make test
make run FILE=lessons/09-multi-agent/multi_agent.py
```

## ポイント解説 / Key points
- **AI Agent vs Agentic AI**: 単一エージェント（lesson 00-05）が「AI Agent」なら、
  この複数エージェントの協調が「Agentic AI」。粒度が一段上がります。
  A single agent is an "AI Agent"; this coordination of several is "Agentic AI".
- 既存パターンの**合成**であることに注目：分解は orchestrator-workers、並列は
  parallelization、`max_parallel` は lesson 07 のガードレール。再実装ではなく組み合わせ。
  Note this *composes* existing patterns rather than reinventing them.
- 各 researcher は**独立したコンテキスト**で走るため、互いの出力に汚染されません。
  これは大きな調査タスクで文脈を清潔に保つ鍵です。Each researcher runs in an isolated
  context — key to keeping large research tasks clean.
- 本番ではここに lesson 05 の可観測性を足し、どの小問が遅い／高コストかを可視化します。
  Add lesson-05 observability in production to see which sub-questions are slow/costly.

## 演習 / Exercise
1. `researcher` に lesson 08 の `retrieve` ツールを与え、RAG で裏取りさせる。
   Give the researcher lesson 08's `retrieve` tool to ground answers via RAG.
2. `max_parallel` を変えて実行時間の差を測る / measure latency vs `max_parallel`.
