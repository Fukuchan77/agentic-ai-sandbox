"""オフラインテスト用の決定論的 LLM / a deterministic LLM for offline tests.

全レッスンのテストが共有します。``CustomLLM`` を継承して ``script`` フィールドを 1 つ足すだけ。
``acomplete`` は基底が ``complete`` に委譲するので、API キーなしでワークフローが決定論的に動きます。

Shared by every lesson's tests. Subclasses ``CustomLLM`` with a single ``script`` field; the base
``acomplete`` delegates to ``complete``, so workflows run deterministically with no API key.
"""

from __future__ import annotations

from collections.abc import Generator

from llama_index.core.llms import CompletionResponse, CustomLLM, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback

__all__ = ["ScriptedLLM"]


class ScriptedLLM(CustomLLM):
    """常に ``script`` の固定テキストを返す / always returns the fixed ``script`` text."""

    script: str = ""

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata()

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: object
    ) -> CompletionResponse:
        return CompletionResponse(text=self.script)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: object
    ) -> Generator[CompletionResponse, None, None]:
        yield CompletionResponse(text=self.script, delta=self.script)
