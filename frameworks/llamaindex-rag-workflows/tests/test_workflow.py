"""イベント駆動 RAG ワークフローのオフラインテスト / offline tests for the RAG workflow.

スクリプト化した ``MockLLM`` を注入するので API キーは不要 / no API key needed.
"""

from __future__ import annotations

from collections.abc import Generator

from llama_index.core.llms import CompletionResponse, CustomLLM, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback

from li_rag_workflows.corpus import retrieve
from li_rag_workflows.workflow import ask


class ScriptedLLM(CustomLLM):
    """常に固定テキストを返す決定論的 LLM / a deterministic LLM that returns fixed text.

    ``CustomLLM`` を継承して ``script`` フィールドを 1 つ足すだけ。``acomplete`` は基底が
    ``complete`` に委譲するので、これでワークフローが決定論的・オフラインで動く。
    Subclasses ``CustomLLM`` with a single ``script`` field; the base ``acomplete``
    delegates to ``complete``, so the workflow runs deterministically and offline.
    """

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


def test_retrieve_is_deterministic_and_relevant() -> None:
    # lesson 08 と同じ不変条件 / same invariant as lesson 08.
    hits = retrieve("テスト api キー")
    assert any(d.id == "doc-2" for d in hits)
    assert len(hits) <= 2


async def test_workflow_returns_grounded_answer() -> None:
    # 実在文書 doc-2 を引用 → 検証を通過して停止 / cites real doc-2 → grounded → stop.
    llm = ScriptedLLM(script="TestModel と FunctionModel を使う。 SOURCES: doc-2")
    result = await ask("テスト api キー", llm=llm)
    assert result.sources == ["doc-2"]
    assert "doc-2" in result.answer


async def test_workflow_streams_progress_events() -> None:
    # 進捗イベントが stream_events() で逐次流れること / progress is streamed.
    msgs: list[str] = []
    llm = ScriptedLLM(script="回答です。 SOURCES: doc-2")
    await ask("テスト api キー", llm=llm, on_progress=msgs.append)
    assert any("検索" in m for m in msgs)  # retrieving
    assert any("生成" in m for m in msgs)  # generating


async def test_ungrounded_citation_triggers_retry_then_gives_up() -> None:
    # 実在しない doc-999 を引用 → 再検索ループ → 上限で打ち切り、根拠ある引用は残らない。
    # Cites a fake doc-999 → retry loop → give up at the cap with no grounded sources.
    msgs: list[str] = []
    llm = ScriptedLLM(script="それは doc-999 に書いてあります。 SOURCES: doc-999")
    result = await ask("RAG とは何ですか", llm=llm, on_progress=msgs.append)
    assert result.sources == []
    assert any("再検索" in m or "re-retrieving" in m for m in msgs)


async def test_no_match_stops_early() -> None:
    # どの文書ともキーワードが重ならない → 早期に「該当なし」で停止 / no overlap → early stop.
    result = await ask("xyzzy", llm=ScriptedLLM(script="(unused)"))
    assert result.sources == []
    assert "該当なし" in result.answer
