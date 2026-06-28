"""Lesson 09 のオフラインテスト / Offline tests for lesson 09.

3 つのエージェントにそれぞれ別の ``TestModel`` を注入し、分割→並列→統合の流れを
決定論的に検証します。Inject a separate ``TestModel`` into each of the three agents
to test decompose → parallel → synthesize deterministically.
"""

from __future__ import annotations

from multi_agent import ResearchReport, deep_research
from pydantic_ai.models.test import TestModel


async def test_pipeline_produces_report() -> None:
    report = await deep_research(
        "observability",
        lead_model=TestModel(custom_output_args={"questions": ["q1", "q2", "q3"]}),
        researcher_model=TestModel(custom_output_text="finding"),
        synth_model=TestModel(custom_output_text="final summary"),
    )
    assert isinstance(report, ResearchReport)
    # lead が出した 3 小問 → 3 findings / 3 sub-questions become 3 findings.
    assert len(report.findings) == 3
    assert {f.question for f in report.findings} == {"q1", "q2", "q3"}
    assert all(f.answer == "finding" for f in report.findings)
    assert report.summary == "final summary"


async def test_bounded_parallelism_still_covers_all() -> None:
    # 同時実行を 1 に絞っても、全小問が調査される（ガードレールは網羅性を壊さない）。
    # Even with max_parallel=1, every sub-question is covered.
    report = await deep_research(
        "topic",
        lead_model=TestModel(custom_output_args={"questions": ["a", "b"]}),
        researcher_model=TestModel(custom_output_text="x"),
        synth_model=TestModel(custom_output_text="s"),
        max_parallel=1,
    )
    assert len(report.findings) == 2
