"""Lesson 05 — 可観測性 / Observability with Logfire.

エージェントは「中で何が起きたか」が見えにくい（どのツールを、どんな引数で呼び、
何トークン使ったか）。Pydantic AI は **Logfire** とネイティブ統合しており、1 行で
全実行をトレースできます。

Agents are hard to observe (which tools ran, with what args, how many tokens?).
Pydantic AI integrates natively with **Logfire**: one line traces every run.

本レッスンは「**任意で**」有効化できる形にしています。``LOGFIRE_ENABLED`` が未設定なら
何もしません（オフラインのテスト・学習を妨げない）。

This lesson makes instrumentation **opt-in**: if ``LOGFIRE_ENABLED`` is unset it
does nothing, so offline tests/learning are never blocked.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


def configure_observability() -> bool:
    """Logfire 計装を（有効なら）設定する / Configure Logfire instrumentation if enabled.

    Returns:
        計装を有効化したかどうか / whether instrumentation was enabled.

    環境変数 / Env:
        ``LOGFIRE_ENABLED=1`` のときだけ Logfire を構成し、``Agent`` 全体を計装します。
        Only when ``LOGFIRE_ENABLED=1`` do we configure Logfire and instrument all agents.
    """
    if os.environ.get("LOGFIRE_ENABLED") != "1":
        return False

    # 遅延 import：無効時は logfire を読み込まない / lazy import when disabled.
    import logfire

    # token があればクラウド送信、無ければローカル表示のみ（ネットワーク不要）。
    # With a token, send to the cloud; otherwise local-only (no network).
    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()  # 以後すべての Agent 実行が自動でトレースされる
    return True


def build_agent(model: Model | None = None) -> Agent[None, str]:
    """計装の有無に関わらず同じエージェント / Same agent, instrumented or not."""
    return Agent(
        model=model or get_model(),
        instructions="あなたは簡潔に答えるアシスタントです。",
    )


def main() -> None:
    enabled = configure_observability()
    print(f"[observability] enabled={enabled}")
    agent = build_agent()
    print(agent.run_sync("可観測性はなぜ重要？一言で。").output)


if __name__ == "__main__":
    main()
