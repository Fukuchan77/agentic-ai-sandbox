"""L04 のオフラインテスト / offline tests for L04（API キー不要 / no API key）."""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from routing import build_routing_graph, run_routing


def test_routing_dispatches_to_classified_specialist() -> None:
    # classify → "billing"、billing 専門家 → 回答文。条件付き辺が billing に分岐する。
    # classify → "billing"; the billing specialist replies. The conditional edge routes to billing.
    model = FakeListChatModel(responses=["billing", "請求について対応します"])
    final = build_routing_graph(model).invoke({"inquiry": "請求書が二重に来ました"})
    assert final["category"] == "billing"
    assert final["answer"] == "請求について対応します"


def test_routing_falls_back_to_other_when_unclassifiable() -> None:
    # 3 カテゴリ語を含まない応答は other に丸められる / unrecognized text falls back to "other".
    model = FakeListChatModel(responses=["わかりません", "一般的にご案内します"])
    assert run_routing("天気はどうですか", model=model) == "一般的にご案内します"
    assert build_routing_graph(model).invoke({"inquiry": "?"})["category"] == "other"
