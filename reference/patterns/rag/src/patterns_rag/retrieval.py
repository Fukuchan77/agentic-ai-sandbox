"""Deterministic top-k retrieval for the RAG lane (Spec 007-2b Req 3.1, 3.3).

A vector retriever's ordering is only weakly defined when scores tie, which would make
top-k -- and therefore the citations grounding an answer -- flaky run-to-run. This module
owns the ADR-5 post-processor: it re-sorts the retriever's results by ``(-score, chunk_id)``
so higher scores come first and equal scores break by ascending ``chunk_id`` (a lane-unique
deterministic key), then truncates to ``top_k`` and reconstructs the ``RetrievedChunk``
contract from each node's ``id_`` / ``metadata`` / content. The same path is used in the
gated Ollama integration lane, so determinism is identical offline and online (NFR-2).

This module does not own index construction or embeddings (:mod:`patterns_rag.indexing`)
or citation validation (:mod:`patterns_rag.citation`).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from patterns_contracts import RetrievedChunk

if TYPE_CHECKING:
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.schema import NodeWithScore

__all__ = ["retrieve"]


def _score_of(scored_node: NodeWithScore) -> float:
    """Return the node's score, treating an absent (``None``) score as ``0.0``.

    A ``None`` score would crash the ``-score`` sort key and has no meaningful order; pinning
    it to ``0.0`` keeps the sort total and lands unscored nodes below any positive match.
    """
    return scored_node.score if scored_node.score is not None else 0.0


def _to_retrieved_chunk(scored_node: NodeWithScore, *, score: float) -> RetrievedChunk:
    """Reconstruct the ``RetrievedChunk`` contract from a retrieved node's metadata.

    The lane's chunks carry ``source`` and ``locator`` in their node metadata (set by
    :mod:`patterns_rag.chunking`); both are required to ground a citation. A node from a
    foreign source that omits either key cannot be turned into a citable chunk, so this
    raises a :class:`KeyError` naming the offending node id and the metadata contract --
    a clear contract breach rather than a bare, context-free ``KeyError`` from ``[...]``.
    """
    node = scored_node.node
    metadata = node.metadata
    missing = [key for key in ("source", "locator") if key not in metadata]
    if missing:
        msg = (
            f"node {node.node_id!r} is missing required metadata {missing}; "
            "the RetrievedChunk contract needs both 'source' and 'locator'."
        )
        raise KeyError(msg)
    return RetrievedChunk(
        chunk_id=node.node_id,
        source=metadata["source"],
        locator=metadata["locator"],
        text=node.get_content(),
        score=score,
    )


async def retrieve(retriever: BaseRetriever, query: str, *, top_k: int = 4) -> list[RetrievedChunk]:
    """Retrieve ``query`` and return the top-k chunks in deterministic order.

    The retriever's own ``retrieve`` call is synchronous and may perform blocking I/O (a
    vector-store query, an embedding round-trip in the integration lane). Because this seam
    is awaited from the async ``run_rag`` hot path, that call is offloaded with
    :func:`asyncio.to_thread` so it never blocks the event loop -- offloading (rather than
    ``aretrieve``) keeps the seam working with sync-only retrievers and the unit-suite stub
    fakes, which implement only synchronous ``_retrieve``. The deterministic sort and
    contract reconstruction are pure CPU and stay on the caller's thread.

    Args:
        retriever: Any LlamaIndex retriever (e.g. ``index.as_retriever(...)``); unit runs
            inject a stub returning fixed nodes.
        query: The natural-language query string.
        top_k: Maximum number of chunks to return, applied *after* the deterministic sort
            so the highest-scoring chunks survive truncation. Must be >= 1.

    Returns:
        Up to ``top_k`` ``RetrievedChunk`` contracts ordered by ``(-score, chunk_id)``:
        descending score, ties broken by ascending ``chunk_id`` (ADR-5, Req 3.3).

    Note:
        The deterministic tiebreak orders the set the retriever *returned*; it does not affect
        which nodes the retriever selected. Operate the retriever with its ``similarity_top_k``
        >= this ``top_k`` so a score tie at the retriever's own cutoff cannot drop a chunk
        before the sort sees it (membership is the retriever's concern, ordering is ours).

    Raises:
        ValueError: If ``top_k`` is less than 1.
        KeyError: If a retrieved node lacks the required ``source`` / ``locator`` metadata.
    """
    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}.")
    nodes = await asyncio.to_thread(retriever.retrieve, query)
    scored = [(_score_of(node), node) for node in nodes]
    scored.sort(key=lambda pair: (-pair[0], pair[1].node.node_id))
    return [_to_retrieved_chunk(node, score=score) for score, node in scored[:top_k]]
