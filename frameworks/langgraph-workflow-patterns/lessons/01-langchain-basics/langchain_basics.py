"""LangGraph トラック L01 — LangChain の基礎 / LangChain basics.

グラフを学ぶ前に、LangChain の最小単位「**チャットモデル**」を押さえます。要点は 3 つ:

Before graphs, learn LangChain's smallest unit — the **chat model**. Three ideas:

1. **メッセージ / Messages** — 会話は ``SystemMessage`` / ``HumanMessage`` などの列で表す。
2. **invoke** — モデルにメッセージ列を渡すと ``AIMessage`` が返る。
3. **プロバイダ非依存 / Provider-agnostic** — ``get_chat_model()`` が ``.env`` を見て
   Anthropic か Ollama の ``BaseChatModel`` を返す（コードは同じ）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage

from lg_workflow_patterns.chat import content_to_text
from lg_workflow_patterns.provider import get_chat_model

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


def one_shot(system: str, user: str, model: BaseChatModel | None = None) -> str:
    """システム指示 + ユーザー入力で 1 回だけ応答を得る / a single system+user turn.

    Args:
        system: モデルへの役割指示 / the role instruction.
        user: ユーザーの入力 / the user input.
        model: 注入する chat model。``None`` なら ``.env`` から構築。テストでは
            ``FakeListChatModel`` を渡せます。Inject a model; ``None`` builds one from ``.env``.
    """
    m = model or get_chat_model()
    # メッセージ列を組み立てて invoke する（これが LangChain の最小呼び出し）/
    # build a message list and invoke — the minimal LangChain call.
    reply = m.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    # content は str か parts のリスト。content_to_text で str に正規化する /
    # content may be str or a list of parts; normalize it.
    return content_to_text(reply.content)


def main() -> None:
    print(one_shot("あなたは簡潔なアシスタント。", "LangChain のチャットモデルとは？"))


if __name__ == "__main__":
    main()
