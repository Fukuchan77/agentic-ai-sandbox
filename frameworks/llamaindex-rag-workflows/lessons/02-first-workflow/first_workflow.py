"""LlamaIndex トラック L02 — 最初の Workflow / your first workflow.

LlamaIndex Workflows の本質は「**イベントを受けてイベントを返すステップ**の連鎖」です。
ここでは LLM を使わず、**仕組み**に集中します。

A LlamaIndex Workflow is a chain of **steps that consume an event and emit one**. To focus on
the *mechanics*, this lesson uses no LLM.

    StartEvent ─▶ shout ─▶ LoudEvent ─▶ exclaim ─▶ StopEvent

要点 / Key ideas:
- ``@step`` を付けた async メソッドが 1 ステップ。引数の **イベント型**で起動条件が決まる。
- ステップは次のイベントを ``return`` する。``StopEvent(result=...)`` で終了し、結果が ``run`` の戻り値に。
"""

from __future__ import annotations

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


class LoudEvent(Event):
    """shout → exclaim へ渡す中間イベント / the intermediate event between steps."""

    loud: str


class EchoWorkflow(Workflow):
    """2 ステップの最小ワークフロー / a minimal two-step workflow."""

    @step
    async def shout(self, ev: StartEvent) -> LoudEvent:
        # StartEvent に渡したキーワード引数は属性として読める / kwargs to run() appear as attrs.
        text = str(getattr(ev, "text", ""))
        return LoudEvent(loud=text.upper())

    @step
    async def exclaim(self, ev: LoudEvent) -> StopEvent:
        return StopEvent(result=ev.loud + "!")


async def run_echo(text: str) -> str:
    """ワークフローを実行して最終結果を返す / run the workflow and return its result."""
    wf = EchoWorkflow(timeout=10)
    return await wf.run(text=text)


def main() -> None:
    import asyncio

    print("result:", asyncio.run(run_echo("hello")))


if __name__ == "__main__":
    main()
