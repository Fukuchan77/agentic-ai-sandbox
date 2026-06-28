"""LLM プロバイダ抽象 / LLM provider abstraction.

このモジュールは、すべてのレッスンが共有する **唯一の** モデル生成口です。
`LLM_PROVIDER` 環境変数を読み、Anthropic（既定）か Ollama（ローカル・無償）の
どちらの ``Model`` を返すかを切り替えます。各レッスンの ``main.py`` は
``get_model()`` を呼ぶだけで、プロバイダの違いを意識しません。

This module is the *single* place every lesson obtains a model from. It reads
the ``LLM_PROVIDER`` environment variable and returns either an Anthropic model
(the default) or an Ollama model (local, free). Lessons just call
``get_model()`` and stay provider-agnostic.

設計方針 / Design rules:
- モデル ID をコードにハードコードしない。すべて ``.env`` から読む。
  Never hardcode model IDs in code — they all come from ``.env``.
- ``.env`` を読み込むため pydantic-settings を使う（型付き・起動時バリデーション）。
  Uses pydantic-settings to load ``.env`` (typed, validated at startup).
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pydantic_ai.models import Model

__all__ = ["BootcampSettings", "get_model", "get_settings"]


class BootcampSettings(BaseSettings):
    """環境変数で駆動するブートキャンプ設定 / Env-driven bootcamp settings.

    ``.env`` ファイル（リポジトリ直下、``.env.example`` からコピー）または
    プロセス環境変数から読み込まれます。

    Loaded from a ``.env`` file (repo root, copied from ``.env.example``) or
    from process environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # どのプロバイダを使うか / Which provider to use.
    llm_provider: Literal["anthropic", "ollama"] = "anthropic"

    # --- Anthropic ---
    # API キー（anthropic 利用時に必須）/ API key (required when using anthropic).
    anthropic_api_key: str | None = None
    # モデル ID。最新世代を既定に。低コスト: claude-haiku-4-5 / 最難: claude-opus-4-8。
    # Model ID. Latest generation by default. Cheaper: claude-haiku-4-5 / hardest: claude-opus-4-8.
    anthropic_model: str = "claude-sonnet-4-6"

    # --- Ollama (ローカル・無償 / local, free) ---
    # OpenAI 互換エンドポイント。末尾の /v1 が必要。
    # OpenAI-compatible endpoint. The trailing /v1 is required.
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"
    ollama_api_key: str | None = None  # 通常は不要 / usually unnecessary


@lru_cache
def get_settings() -> BootcampSettings:
    """設定を一度だけ読み込んでキャッシュする / Load settings once and cache them."""
    return BootcampSettings()


def get_model() -> Model:
    """設定に従って ``Model`` を構築して返す / Build and return a ``Model`` per settings.

    Returns:
        ``pydantic_ai.models.Model`` 実装。``Agent(model=...)`` にそのまま渡せます。
        A ``pydantic_ai.models.Model`` implementation, ready for ``Agent(model=...)``.

    Raises:
        ValueError: ``anthropic`` を選んだのに ``ANTHROPIC_API_KEY`` が無い場合。
            When ``anthropic`` is selected but ``ANTHROPIC_API_KEY`` is missing.

    Note:
        モデル構築は純粋（ネットワーク通信なし）です。実際の HTTP は ``agent.run(...)``
        まで遅延されます。Model construction is pure (no network I/O); the actual
        HTTP round-trip is deferred until ``agent.run(...)``.
    """
    settings = get_settings()

    if settings.llm_provider == "anthropic":
        # 遅延 import：ollama だけ使う人に anthropic SDK の import を強制しない。
        # Lazy import so Ollama-only users don't pay the anthropic SDK import.
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai.providers.anthropic import AnthropicProvider

        if not settings.anthropic_api_key:
            msg = (
                "LLM_PROVIDER=anthropic ですが ANTHROPIC_API_KEY が未設定です。"
                " .env に設定するか LLM_PROVIDER=ollama に切り替えてください。 / "
                "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is unset."
                " Set it in .env or switch to LLM_PROVIDER=ollama."
            )
            raise ValueError(msg)

        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
        return AnthropicModel(settings.anthropic_model, provider=provider)

    # settings.llm_provider == "ollama"
    from pydantic_ai.models.ollama import OllamaModel
    from pydantic_ai.providers.ollama import OllamaProvider

    provider = OllamaProvider(
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key,
    )
    return OllamaModel(settings.ollama_model, provider=provider)
