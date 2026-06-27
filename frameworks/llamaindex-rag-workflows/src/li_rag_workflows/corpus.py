"""知識ベースと決定論的検索 / the knowledge base and deterministic retrieval.

Lesson 08（``lessons/08-rag/rag.py``）からそのまま移植。埋め込みを使わず**キーワード一致**で
検索します（考え方はベクトル検索と同じ）。本物の RAG ではこの ``retrieve`` を
LlamaIndex の ``VectorStoreIndex`` に差し替えるだけで、インターフェースは変わりません。

Ported verbatim from Lesson 08. Retrieval is **keyword overlap** (no embeddings); the
idea is identical to vector search. For real RAG, swap ``retrieve`` for a
``VectorStoreIndex`` — the interface ``retrieve(query) -> docs`` is unchanged.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Doc:
    """知識ベースの 1 文書 / one document in the knowledge base."""

    id: str
    text: str


# 小さな知識ベース / a tiny knowledge base（lesson 08 と同一）.
CORPUS: tuple[Doc, ...] = (
    Doc("doc-1", "Pydantic AI は型付き出力と検証を中心に据えた Python のエージェント框架です。"),
    Doc(
        "doc-2", "TestModel と FunctionModel を使うと API キーなしでエージェントをテストできます。"
    ),
    Doc("doc-3", "RAG は検索した文書を文脈に加え、引用付きで回答を生成する手法です。"),
    Doc("doc-4", "ツールは RunContext を第一引数に取ると依存性（deps）へアクセスできます。"),
)

VALID_IDS = frozenset(d.id for d in CORPUS)


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.lower()))


def retrieve(query: str, k: int = 2) -> list[Doc]:
    """キーワード一致で上位 k 件を返す / return top-k docs by keyword overlap."""
    q = _tokenize(query)
    scored = sorted(CORPUS, key=lambda d: len(q & _tokenize(d.text)), reverse=True)
    # 重なりが 0 の文書は除外 / drop docs with zero overlap.
    return [d for d in scored if q & _tokenize(d.text)][:k]
