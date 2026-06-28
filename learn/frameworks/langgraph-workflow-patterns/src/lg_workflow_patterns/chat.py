"""チャット呼び出しの共有ヘルパ / shared chat helpers.

各レッスンが共通で使う 2 つの小道具を 1 か所に置きます。レッスン本体は「グラフの構造」に
集中でき、メッセージ整形やバージョン差吸収のノイズをここへ追い出せます。

Two small utilities every lesson reuses, kept in one place so the lessons can focus on
*graph structure* rather than message plumbing and version quirks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage

from lg_workflow_patterns.provider import get_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

__all__ = ["ask", "content_to_text", "get_chat_model"]


def content_to_text(content: object) -> str:
    """``AIMessage.content`` を文字列に正規化する / normalize message content to a string.

    LangChain のバージョンにより ``content`` は「文字列」か「テキストパーツのリスト」の
    どちらか。どちらでも壊れないよう両対応します。Content may be a string or a list of
    parts depending on the LangChain version; handle both.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [p.get("text", "") if isinstance(p, dict) else str(p) for p in content]
        return "".join(parts)
    return str(content)


def ask(model: BaseChatModel, system: str, user: str) -> str:
    """system + user の 1 ターンを実行して本文テキストを返す / one chat turn → text.

    LangChain の chat model は ``BaseMessage`` のリストを受け取ります。ここでは最小構成の
    「システム指示 + ユーザー入力」を渡します。A chat model takes a list of ``BaseMessage``;
    here we pass a minimal system + user pair.
    """
    reply = model.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return content_to_text(reply.content)
