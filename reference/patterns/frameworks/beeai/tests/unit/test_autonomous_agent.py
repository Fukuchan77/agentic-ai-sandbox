"""Autonomous-agent unit tests — BeeAI lane (Spec 006-2a Req 6.1-6.6, 7.2/7.3, 9.1/9.2, 10.3).

These tests exercise ``run_autonomous_agent`` fully offline. The loop is a manual
tool loop on BeeAI chat primitives (``llm.create``), so the support
``TurnSequencedChatModel`` (Task 4.2) replays a scripted ``tool call → final
answer`` sequence via an internal call cursor — BeeAI exposes no tool-return
history at the model boundary, so the fake advances per ``create`` rather than by
counting history entries (the pydantic-ai lane difference, plan line 165).
``StubTool`` is the deterministic in-memory tool. Each scripted turn carries a
fixed token count surfaced on ``ChatModelOutput.usage``, so the ``_budget_spent``
seam — and therefore the ``budget_exceeded`` guardrail — fires deterministically.

The four contract-level guardrails (Req 10.3 defense-in-depth) each get a
violation test: allowed-tools refusal (6.4), human-approval denial (6.5), budget
overrun (6.6), and the ``max_iterations`` cutoff (6.3), plus the happy path.

Observability for the BeeAI lane is the manual-span fallback (Req 9.1): the span
test wraps the run with :func:`patterns_beeai.observability.traced`, mirroring
``test_evaluator_optimizer.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from patterns_beeai.autonomous_agent import run_autonomous_agent
from patterns_beeai.observability import configure_tracing, traced
from tests.support.fake_chat_model import (
    FinalTurn,
    StubTool,
    ToolTurn,
    TurnSequencedChatModel,
)


def _approve_all(_tool: str, _args: str) -> bool:
    """Approval hook that approves every dangerous tool call."""
    return True


def _deny_all(_tool: str, _args: str) -> bool:
    """Approval hook that denies every dangerous tool call."""
    return False


@dataclass
class _RecordingTool:
    """Tool (contracts ``Tool`` Protocol) that records the args string it ran with."""

    name: str
    received: list[str] = field(default_factory=list[str])
    dangerous: bool = False

    def run(self, args: str) -> str:
        """Record ``args`` and return a fixed observation."""
        self.received.append(args)
        return "recorded"


async def test_completes_with_final_answer_after_tool_call() -> None:
    # Req 6.1/6.2: a tool call followed by a final answer completes the loop,
    # recording the executed step with the tool's observation and per-turn
    # budget, and stopping with stop_reason="completed".
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="lookup", args="q", tokens=3),
            FinalTurn(text="the answer is 42", tokens=2),
        ]
    )

    result = await run_autonomous_agent(
        "find the answer",
        llm=llm,
        max_iterations=5,
        allowed_tools=[StubTool(name="lookup", observation="42")],
        approval_hook=_approve_all,
        budget=100,
    )

    assert result.stop_reason == "completed"
    assert result.final_output == "the answer is 42"
    assert len(result.steps) == 1
    assert result.steps[0].index == 0
    assert result.steps[0].tool == "lookup"
    assert result.steps[0].observation == "42"
    assert result.steps[0].budget_spent == 3
    # Every turn's spend is accumulated once up front, so total_budget_spent
    # includes the final (no-tool-call) turn's tokens too: 3 (tool) + 2 (final).
    assert result.total_budget_spent == 5


async def test_forwards_tool_call_args_to_the_tool() -> None:
    # Req 6.1: the loop forwards the model's tool-call args verbatim to Tool.run
    # (BeeAI surfaces args as a plain string, so no normalization is needed) and
    # records the tool-produced observation.
    tool = _RecordingTool(name="edit")
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="edit", args="path=a", tokens=1),
            FinalTurn(text="done", tokens=1),
        ]
    )

    result = await run_autonomous_agent(
        "edit files",
        llm=llm,
        max_iterations=5,
        allowed_tools=[tool],
        approval_hook=_approve_all,
        budget=100,
    )

    assert result.stop_reason == "completed"
    assert tool.received == ["path=a"]
    assert result.steps[0].observation == "recorded"


async def test_stops_with_disallowed_tool_outside_allowed_list() -> None:
    # Req 6.4 (least privilege): a call to a tool absent from allowed_tools is
    # refused — never executed — the refused attempt is recorded, and the loop
    # stops with stop_reason="disallowed_tool" (a hard stop, distinct from
    # denied). Only the disallowed turn is scripted: if the loop wrongly
    # continued it would request a second turn and the fake would fail loudly.
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="shell", args="rm -rf /", tokens=1),
        ]
    )

    result = await run_autonomous_agent(
        "do the task",
        llm=llm,
        max_iterations=5,
        allowed_tools=[StubTool(name="search", observation="results")],
        approval_hook=_approve_all,
        budget=100,
    )

    assert result.stop_reason == "disallowed_tool"
    assert result.final_output is None
    assert len(result.steps) == 1
    assert result.steps[0].tool == "shell"
    # The refused tool was not executed: the observation is the refusal marker,
    # never a tool-produced observation.
    assert "not in allowed_tools" in result.steps[0].observation


async def test_stops_with_denied_when_approval_hook_rejects_dangerous_tool() -> None:
    # Req 6.5: a dangerous tool whose approval_hook returns False is not
    # executed; the loop stops with stop_reason="denied" and no final_output.
    llm = TurnSequencedChatModel([ToolTurn(tool="deploy", args="prod", tokens=2)])

    result = await run_autonomous_agent(
        "ship it",
        llm=llm,
        max_iterations=5,
        allowed_tools=[StubTool(name="deploy", observation="deployed", dangerous=True)],
        approval_hook=_deny_all,
        budget=100,
    )

    assert result.stop_reason == "denied"
    assert result.final_output is None
    assert len(result.steps) == 1
    assert result.steps[0].tool == "deploy"
    # Not executed: the canned "deployed" observation must never appear.
    assert result.steps[0].observation != "deployed"
    assert result.total_budget_spent == 2


async def test_stops_with_budget_exceeded_before_running_over_budget_tool() -> None:
    # Req 6.6 (unbounded-consumption guard): each turn spends 3 tokens; with a
    # budget of 5 the cumulative spend crosses the cap on the second turn. The
    # budget guardrail is the highest-priority stop, so the loop returns
    # budget_exceeded BEFORE resolving or running the second turn's tool — no
    # step is recorded for the over-budget turn, and the over-budget tool's side
    # effect never fires. total_budget_spent equals the accumulated spend (6).
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="probe", args="a", tokens=3),
            ToolTurn(tool="probe", args="b", tokens=3),
            FinalTurn(text="unreached", tokens=1),
        ]
    )

    result = await run_autonomous_agent(
        "keep probing",
        llm=llm,
        max_iterations=10,
        allowed_tools=[StubTool(name="probe", observation="ok")],
        approval_hook=_approve_all,
        budget=5,
    )

    assert result.stop_reason == "budget_exceeded"
    assert result.final_output is None
    # Only the first (within-budget) turn ran; the over-budget turn stopped
    # before a step was appended.
    assert len(result.steps) == 1
    assert result.steps[0].tool == "probe"
    assert result.steps[0].observation == "ok"
    assert result.total_budget_spent == 6


async def test_budget_exceeded_does_not_execute_the_over_budget_tool() -> None:
    # Req 6.6 intent: the budget guardrail must pre-empt the side effect. The
    # second turn pushes cumulative spend past the budget, so the loop must stop
    # before invoking the (recording) tool — the tool records nothing for the
    # over-budget turn.
    tool = _RecordingTool(name="probe")
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="probe", args="a", tokens=3),
            ToolTurn(tool="probe", args="b", tokens=3),
        ]
    )

    result = await run_autonomous_agent(
        "keep probing",
        llm=llm,
        max_iterations=10,
        allowed_tools=[tool],
        approval_hook=_approve_all,
        budget=5,
    )

    assert result.stop_reason == "budget_exceeded"
    # The first turn ran the tool once; the over-budget second turn never did.
    assert tool.received == ["a"]


async def test_stops_at_max_iterations_when_loop_never_finalizes() -> None:
    # Req 6.3: a loop that keeps requesting tools without ever producing a final
    # answer stops at max_iterations with no final_output.
    llm = TurnSequencedChatModel(
        [
            ToolTurn(tool="probe", args="a", tokens=1),
            ToolTurn(tool="probe", args="b", tokens=1),
        ]
    )

    result = await run_autonomous_agent(
        "loop forever",
        llm=llm,
        max_iterations=2,
        allowed_tools=[StubTool(name="probe", observation="ok")],
        approval_hook=_approve_all,
        budget=100,
    )

    assert result.stop_reason == "max_iterations"
    assert result.final_output is None
    assert len(result.steps) == 2
    assert result.total_budget_spent == 2


async def test_rejects_non_positive_iteration_cap() -> None:
    # max_iterations < 1 would run zero iterations and silently produce an empty
    # agent run; reject it loudly instead.
    llm = TurnSequencedChatModel([FinalTurn(text="unused", tokens=0)])
    with pytest.raises(ValueError, match="max_iterations must be"):
        await run_autonomous_agent(
            "task",
            llm=llm,
            max_iterations=0,
            allowed_tools=[],
            approval_hook=_approve_all,
            budget=10,
        )


async def test_rejects_negative_budget() -> None:
    # A negative budget is nonsensical for an unbounded-consumption guardrail and
    # would make every run trip budget_exceeded; reject it loudly.
    llm = TurnSequencedChatModel([FinalTurn(text="unused", tokens=0)])
    with pytest.raises(ValueError, match="budget must be"):
        await run_autonomous_agent(
            "task",
            llm=llm,
            max_iterations=3,
            allowed_tools=[],
            approval_hook=_approve_all,
            budget=-1,
        )


async def test_autonomous_agent_emits_spans_into_injected_exporter() -> None:
    # Req 9.1/9.2: an instrumented run emits at least one span. The BeeAI lane
    # uses the manual-span fallback, so the caller wraps the run in traced.
    exporter = InMemorySpanExporter()
    provider = configure_tracing(exporter)
    llm = TurnSequencedChatModel([FinalTurn(text="done", tokens=1)])

    result = await traced(
        provider,
        "pattern.autonomous_agent",
        run_autonomous_agent(
            "hello",
            llm=llm,
            max_iterations=2,
            allowed_tools=[],
            approval_hook=_approve_all,
            budget=10,
        ),
    )

    assert result.stop_reason == "completed"
    spans = exporter.get_finished_spans()
    assert spans, "instrumented autonomous-agent run must emit at least one span"
    # Req 9.3: assert only that the (manual pattern-level) span exists; token
    # aggregation is the backend's concern (double-counting trap).
    assert any(span.name == "pattern.autonomous_agent" for span in spans)
