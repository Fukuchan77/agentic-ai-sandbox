"""LLM プロバイダ抽象（LangChain 版）/ LLM provider abstraction (LangChain flavor).

既存教材の ``src/bootcamp_common/provider.py`` と **同じ ``.env`` ・同じ変数名** を読みますが、
返すのは Pydantic AI の ``Model`` ではなく **LangChain の chat model**（``BaseChatModel``）です。
これにより本トラックは ``bootcamp_common`` に一切依存せず、完全に独立して動きます。

Reads the **same ``.env`` and the same variable names** as the bootcamp's
``provider.py``, but returns a **LangChain chat model** (``BaseChatModel``) rather
than a Pydantic AI ``Model``. This keeps the track independent of ``bootcamp_common``.

設計方針 / Design rules（既存教材を踏襲 / mirrors the bootcamp）:
- モデル ID はハードコードしない。すべて ``.env`` から / never hardcode model IDs.
- ``ollama`` は OpenAI 互換エンドポイント（末尾 ``/v1``）経由で到達 / Ollama via its OpenAI-compatible API.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

__all__ = ["LangGraphSettings", "get_chat_model", "get_settings"]


class LangGraphSettings(BaseSettings):
    """環境変数で駆動する設定 / env-driven settings.

    リポジトリ直下の ``.env``（``.env.example`` からコピー）から読み込みます。
    既存教材とキーを共有するので、``.env`` は 1 つで全トラックを賄えます。

    Loaded from the repo-root ``.env`` (copied from ``.env.example``). Keys are
    shared with the bootcamp, so a single ``.env`` powers every track.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["anthropic", "ollama"] = "anthropic"

    # --- Anthropic ---
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Ollama (ローカル・無償 / local, free) ---
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"
    ollama_api_key: str | None = None


@lru_cache
def get_settings() -> LangGraphSettings:
    """設定を一度だけ読み込んでキャッシュする / load settings once and cache them."""
    return LangGraphSettings()


def get_chat_model() -> BaseChatModel:
    """設定に従って LangChain の chat model を構築する / build a LangChain chat model per settings.

    Returns:
        ``langchain_core.language_models.BaseChatModel``。グラフのノードから ``.invoke`` できます。
        A ``BaseChatModel`` the graph nodes can ``.invoke``.

    Raises:
        ValueError: ``anthropic`` を選んだのに ``ANTHROPIC_API_KEY`` が無い場合 /
            when ``anthropic`` is selected but the key is missing.
    """
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        # 遅延 import：ollama だけ使う人に anthropic 依存を強制しない /
        # lazy import so Ollama-only users don't pay the anthropic import.
        from langchain_anthropic import ChatAnthropic

        if not settings.anthropic_api_key:
            msg = (
                "LLM_PROVIDER=anthropic ですが ANTHROPIC_API_KEY が未設定です。"
                " .env に設定するか LLM_PROVIDER=ollama に切り替えてください。 / "
                "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is unset."
                " Set it in .env or switch to LLM_PROVIDER=ollama."
            )
            raise ValueError(msg)

        return ChatAnthropic(model=settings.anthropic_model, api_key=settings.anthropic_api_key)

    # settings.llm_provider == "ollama"
    # Ollama の OpenAI 互換エンドポイントへ向ける / point the OpenAI client at Ollama.
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key or "ollama",  # ダミーキーで可 / a dummy key is fine.
    )
