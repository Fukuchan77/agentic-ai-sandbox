"""LLM プロバイダ抽象（LlamaIndex 版）/ LLM provider abstraction (LlamaIndex flavor).

既存教材の ``provider.py`` と **同じ ``.env`` ・同じ変数名** を読みますが、返すのは
**LlamaIndex の ``LLM``** です。``bootcamp_common`` には依存しません。

Reads the **same ``.env`` and variable names** as the bootcamp's ``provider.py`` but
returns a **LlamaIndex ``LLM``**. Independent of ``bootcamp_common``.

設計方針 / Design rules（既存教材を踏襲 / mirrors the bootcamp）:
- モデル ID はハードコードしない / never hardcode model IDs.
- ``ollama`` は OpenAI 互換エンドポイント（末尾 ``/v1``）経由 / Ollama via its OpenAI-compatible API.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from llama_index.core.llms import LLM

__all__ = ["LlamaIndexSettings", "get_llm", "get_settings"]


class LlamaIndexSettings(BaseSettings):
    """環境変数で駆動する設定 / env-driven settings（既存教材とキー共有）."""

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
def get_settings() -> LlamaIndexSettings:
    """設定を一度だけ読み込んでキャッシュする / load settings once and cache them."""
    return LlamaIndexSettings()


def get_llm() -> LLM:
    """設定に従って LlamaIndex の ``LLM`` を構築する / build a LlamaIndex ``LLM`` per settings.

    Raises:
        ValueError: ``anthropic`` を選んだのに ``ANTHROPIC_API_KEY`` が無い場合 /
            when ``anthropic`` is selected but the key is missing.
    """
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        # 遅延 import / lazy import.
        from llama_index.llms.anthropic import Anthropic

        if not settings.anthropic_api_key:
            msg = (
                "LLM_PROVIDER=anthropic ですが ANTHROPIC_API_KEY が未設定です。"
                " .env に設定するか LLM_PROVIDER=ollama に切り替えてください。 / "
                "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is unset."
                " Set it in .env or switch to LLM_PROVIDER=ollama."
            )
            raise ValueError(msg)

        return Anthropic(model=settings.anthropic_model, api_key=settings.anthropic_api_key)

    # settings.llm_provider == "ollama" — OpenAI 互換クライアントを Ollama に向ける。
    from llama_index.llms.openai_like import OpenAILike

    return OpenAILike(
        model=settings.ollama_model,
        api_base=settings.ollama_base_url,
        api_key=settings.ollama_api_key or "ollama",  # ダミーキーで可 / a dummy key is fine.
        is_chat_model=True,
    )
