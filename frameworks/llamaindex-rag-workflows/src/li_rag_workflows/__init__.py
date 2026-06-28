"""LlamaIndex 学習トラックの共有パッケージ / shared package for the LlamaIndex track.

実際の教材は ``lessons/NN-*/`` にあります（基礎 → イベント駆動 RAG）。このパッケージは全レッスンが
共有する小道具だけを持ちます：``provider``（``.env`` から LLM を構築）、``corpus``（知識ベース +
キーワード検索）、``testing``（オフライン用の決定論 LLM）。

The lessons live in ``lessons/NN-*/`` (basics → event-driven RAG). This package holds only the
utilities every lesson shares: ``provider`` (builds an LLM from ``.env``), ``corpus`` (the
knowledge base + keyword retrieval), and ``testing`` (a deterministic LLM for offline tests).
"""

from __future__ import annotations

from li_rag_workflows.corpus import CORPUS, VALID_IDS, Doc, retrieve
from li_rag_workflows.provider import get_llm
from li_rag_workflows.testing import ScriptedLLM

__all__ = ["CORPUS", "VALID_IDS", "Doc", "ScriptedLLM", "get_llm", "retrieve"]
