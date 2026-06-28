"""LlamaIndex トラック L04 — イベント駆動 RAG / event-driven RAG (the capstone).

L02（ステップ・イベント）と L03（ストリーミング）を組み合わせ、本体
[Lesson 08](../../../../lessons/08-rag/) の「検索 → 生成 → 引用検証」を**イベント駆動の複数ステップ**
として書き直します。引用が根拠に一致しなければ ``RetryEvent`` を投げて**検索からやり直す**——これが
lesson 08 の ``ModelRetry`` のイベント駆動版です。

Combining L02 (steps & events) and L03 (streaming), this re-implements Lesson 08's
"retrieve → generate → verify" as an **event-driven** workflow. Ungrounded citations raise a
``RetryEvent`` that **retries from retrieval** — the event-driven counterpart of ``ModelRetry``.

    StartEvent ─▶ retrieve ─▶ GenerateEvent ─▶ generate ─▶ VerifyEvent ─▶ verify ─┬▶ StopEvent
                    ▲                                                              │
                    └──────────────── re_retrieve ◀── RetryEvent ◀────────────────┘
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from li_rag_workflows.corpus import VALID_IDS, retrieve
from li_rag_workflows.provider import get_llm

if TYPE_CHECKING:
    from llama_index.core.llms import LLM

# 検証に失敗したとき検索からやり直す最大回数 / max retrieve→generate→verify rounds.
MAX_ATTEMPTS = 2


# --- 公開する結果型 / public result type ------------------------------------
@dataclass(frozen=True)
class RagResult:
    """根拠付きの最終回答 / the final grounded answer（lesson 08 の RagAnswer 相当）."""

    answer: str
    sources: list[str] = field(default_factory=list)


# --- ステップ間を流れるイベント / events that flow between steps --------------
class ProgressEvent(Event):
    """``stream_events()`` で逐次取り出す進捗イベント / streamed progress event."""

    msg: str


class GenerateEvent(Event):
    """検索済み文脈を生成ステップへ渡す / hand retrieved context to the generate step."""

    query: str
    attempt: int
    hit_ids: list[str]
    context_text: str


class VerifyEvent(Event):
    """生成結果を検証ステップへ渡す / hand the draft answer to the verify step."""

    query: str
    attempt: int
    hit_ids: list[str]
    answer: str
    cited: list[str]


class RetryEvent(Event):
    """検証失敗 → 検索からやり直し / verification failed → retry from retrieval."""

    query: str
    attempt: int


def _format(hit_ids_and_text: list[tuple[str, str]]) -> str:
    """検索ヒットをプロンプト用の文脈テキストに整形 / format hits into prompt context."""
    return "\n".join(f"[{doc_id}] {text}" for doc_id, text in hit_ids_and_text)


class RagWorkflow(Workflow):
    """イベント駆動の RAG ワークフロー / the event-driven RAG workflow.

    Args:
        llm: 注入する LlamaIndex ``LLM``。``None`` なら ``.env`` から構築。テストでは
            ``li_rag_workflows.testing.ScriptedLLM`` を渡せます。Inject an ``LLM``; ``None``
            builds one from ``.env``. Tests pass a ``ScriptedLLM``.
    """

    def __init__(self, llm: LLM | None = None, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._llm = llm  # 遅延構築 / built lazily on first use.

    @property
    def llm(self) -> LLM:
        if self._llm is None:
            self._llm = get_llm()
        return self._llm

    # --- 検索（初回）/ retrieval (first attempt) ----------------------------
    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> GenerateEvent | StopEvent:
        query = getattr(ev, "query", "")
        return self._retrieve(ctx, query, attempt=1)

    # --- 検索（リトライ）/ retrieval (retry) --------------------------------
    @step
    async def re_retrieve(self, ctx: Context, ev: RetryEvent) -> GenerateEvent | StopEvent:
        ctx.write_event_to_stream(
            ProgressEvent(msg=f"♻️ 再検索 attempt={ev.attempt} / re-retrieving")
        )
        # 取得幅を広げて再挑戦 / broaden k on retry.
        return self._retrieve(ctx, ev.query, attempt=ev.attempt, k=4)

    def _retrieve(
        self, ctx: Context, query: str, attempt: int, k: int = 2
    ) -> GenerateEvent | StopEvent:
        ctx.write_event_to_stream(ProgressEvent(msg=f"🔎 検索中 / retrieving: {query!r}"))
        hits = retrieve(query, k=k)
        if not hits:
            ctx.write_event_to_stream(ProgressEvent(msg="∅ 該当なし / no matches"))
            return StopEvent(result=RagResult(answer="(該当なし / no matches)", sources=[]))
        ctx.write_event_to_stream(
            ProgressEvent(msg=f"📚 {len(hits)} 件ヒット / hits: {[d.id for d in hits]}")
        )
        return GenerateEvent(
            query=query,
            attempt=attempt,
            hit_ids=[d.id for d in hits],
            context_text=_format([(d.id, d.text) for d in hits]),
        )

    # --- 生成 + トークンのストリーミング / generation + token streaming -------
    @step
    async def generate(self, ctx: Context, ev: GenerateEvent) -> VerifyEvent:
        prompt = (
            "次の文脈だけに基づいて質問に答えてください。"
            "根拠にした文書 ID を最後に `SOURCES: doc-x, doc-y` の形で必ず列挙してください。\n\n"
            f"=== 文脈 ===\n{ev.context_text}\n\n"
            f"=== 質問 ===\n{ev.query}\n"
        )
        ctx.write_event_to_stream(ProgressEvent(msg="✍️ 生成中 / generating"))
        resp = await self.llm.acomplete(prompt)
        answer = str(resp)

        # 生成テキストをトークン単位でストリームに流す（データのストリーミング実演）/
        # stream the answer token-by-token (demonstrates data streaming).
        for tok in answer.split():
            ctx.write_event_to_stream(ProgressEvent(msg=f"· {tok}"))

        cited = re.findall(r"doc-\d+", answer)
        return VerifyEvent(
            query=ev.query,
            attempt=ev.attempt,
            hit_ids=ev.hit_ids,
            answer=answer,
            cited=cited,
        )

    # --- 引用検証（成功なら停止 / 失敗ならリトライ）/ citation guard ----------
    @step
    async def verify(self, ctx: Context, ev: VerifyEvent) -> StopEvent | RetryEvent:
        # 引用が「実在 (VALID_IDS)」かつ「実際に検索でヒットした文書」を指しているか。
        # Citations must be real (VALID_IDS) AND among the docs we actually retrieved.
        allowed = set(ev.hit_ids) & VALID_IDS
        grounded = [c for c in ev.cited if c in allowed]
        bad = [c for c in ev.cited if c not in allowed]

        if grounded and not bad:
            ctx.write_event_to_stream(ProgressEvent(msg=f"✅ 検証OK / grounded: {grounded}"))
            return StopEvent(result=RagResult(answer=ev.answer, sources=grounded))

        # 根拠のない引用 → 再検索（lesson 08 の ModelRetry 相当）/ ungrounded → retry.
        ctx.write_event_to_stream(
            ProgressEvent(msg=f"⚠️ 根拠なし引用 / ungrounded citations: {bad or '(none)'}")
        )
        if ev.attempt >= MAX_ATTEMPTS:
            # 上限到達：根拠のある引用だけ残して打ち切る / give up: keep only grounded citations.
            return StopEvent(
                result=RagResult(answer=ev.answer, sources=grounded),
            )
        return RetryEvent(query=ev.query, attempt=ev.attempt + 1)


async def ask(
    question: str,
    llm: LLM | None = None,
    on_progress: object = None,
) -> RagResult:
    """ワークフローを実行し、進捗をストリーミングしつつ最終結果を返す / run and stream.

    Args:
        question: 質問 / the question.
        llm: 注入する LLM（テスト用）/ inject an LLM (for tests).
        on_progress: ``ProgressEvent.msg`` を受け取る callable（``print`` 等）。``None`` なら無視。
            A callable receiving each ``ProgressEvent.msg`` (e.g. ``print``); ``None`` ignores.
    """
    wf = RagWorkflow(llm=llm, timeout=60)
    handler = wf.run(query=question)
    async for ev in handler.stream_events():
        if isinstance(ev, ProgressEvent) and callable(on_progress):
            on_progress(ev.msg)
    return await handler


def main() -> None:
    import asyncio

    result = asyncio.run(ask("Pydantic AI をテストするには？", on_progress=print))
    print("\n--- answer ---")
    print(result.answer)
    print("sources:", result.sources)


if __name__ == "__main__":
    main()
