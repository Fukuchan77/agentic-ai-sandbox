"""LangGraph 学習トラックの共有パッケージ / shared package for the LangGraph track.

実際の教材は ``lessons/NN-*/`` にあります（基礎 → 比較）。このパッケージは全レッスンが
共有する小道具だけを持ちます：``provider``（``.env`` から chat model を構築）と ``chat``
（メッセージ整形ヘルパ）。

The lessons live in ``lessons/NN-*/`` (basics → comparison). This package holds only the
utilities every lesson shares: ``provider`` (builds a chat model from ``.env``) and ``chat``
(message helpers).
"""

from __future__ import annotations

from lg_workflow_patterns.chat import ask, content_to_text
from lg_workflow_patterns.provider import get_chat_model

__all__ = ["ask", "content_to_text", "get_chat_model"]
