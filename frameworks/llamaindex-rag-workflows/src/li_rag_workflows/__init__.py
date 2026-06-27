"""LlamaIndex Workflows 版 RAG / RAG with LlamaIndex Workflows.

Lesson 08（``lessons/08-rag/``）の「検索 → 生成 → 引用検証」を、Pydantic AI のエージェント
ループではなく **LlamaIndex のイベント駆動 Workflows** で書き直した独立トラックです。
各ステップは ``Event`` を受けて ``Event`` を返し、途中経過は ``stream_events()`` で
**ストリーミング**できます。引用検証は ``Event`` の再投入による**ループ**で表現します。

A standalone track that rewrites Lesson 08's "retrieve → generate → verify" as an
**event-driven LlamaIndex Workflow**. Each step consumes an ``Event`` and emits one;
progress is **streamed** via ``stream_events()``; citation checking is expressed as an
event-driven **retry loop**.
"""

from __future__ import annotations

from li_rag_workflows.corpus import CORPUS, VALID_IDS, Doc, retrieve
from li_rag_workflows.workflow import (
    ProgressEvent,
    RagResult,
    RagWorkflow,
    ask,
)

__all__ = [
    "CORPUS",
    "VALID_IDS",
    "Doc",
    "ProgressEvent",
    "RagResult",
    "RagWorkflow",
    "ask",
    "retrieve",
]
