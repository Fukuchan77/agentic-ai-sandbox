"""LlamaIndex トラック L01 — LlamaIndex の基礎 / LlamaIndex basics.

Workflows を学ぶ前に、LlamaIndex の最小単位「**LLM 抽象**」を押さえます。要点は 2 つ:

Before Workflows, learn LlamaIndex's smallest unit — the **LLM abstraction**. Two ideas:

1. **complete / acomplete** — プロンプト文字列を渡すと ``CompletionResponse`` が返る。
   ``str(resp)`` で本文テキストを取り出せる。
2. **プロバイダ非依存 / Provider-agnostic** — ``get_llm()`` が ``.env`` を見て Anthropic か
   Ollama（OpenAI 互換）の ``LLM`` を返す（コードは同じ）。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from li_rag_workflows.provider import get_llm

if TYPE_CHECKING:
    from llama_index.core.llms import LLM


async def one_shot(prompt: str, llm: LLM | None = None) -> str:
    """プロンプトを 1 回投げて本文テキストを返す / a single completion → text.

    Args:
        prompt: モデルへの入力 / the input prompt.
        llm: 注入する LLM。``None`` なら ``.env`` から構築。テストでは ``ScriptedLLM`` を渡せます。
            Inject an LLM; ``None`` builds one from ``.env``. Tests pass a ``ScriptedLLM``.
    """
    m = llm or get_llm()
    # 非同期で完了を得る（Workflows も async なので acomplete を使う）/
    # await the completion (Workflows are async, so we use acomplete).
    resp = await m.acomplete(prompt)
    return str(resp)


def main() -> None:
    import asyncio

    print(asyncio.run(one_shot("LlamaIndex の LLM 抽象とは？一言で。")))


if __name__ == "__main__":
    main()
