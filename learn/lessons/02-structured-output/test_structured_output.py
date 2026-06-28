"""Lesson 02 のオフラインテスト / Offline tests for lesson 02.

``TestModel`` の ``custom_output_args`` で、出力を **決定論的に** 固定できます。
これで構造化出力を扱うコードを安定してテストできます。

``TestModel(custom_output_args=...)`` pins the output **deterministically**,
so code that consumes structured output can be tested reliably.
"""

from __future__ import annotations

from pydantic_ai.models.test import TestModel
from structured_output import CityInfo, describe_city


def test_returns_validated_model() -> None:
    model = TestModel(
        custom_output_args={
            "name": "Kyoto",
            "country": "Japan",
            "population_millions": 1.46,
            "famous_for": ["temples", "gardens"],
        }
    )
    info = describe_city("Kyoto", model=model)
    assert isinstance(info, CityInfo)
    assert info.country == "Japan"
    assert info.population_millions == 1.46
    assert "temples" in info.famous_for


def test_testmodel_autogenerates_valid_instance() -> None:
    # custom_output_args を渡さなくても、TestModel はスキーマに沿う例を生成する。
    # Even without custom args, TestModel generates a schema-valid example.
    info = describe_city("anywhere", model=TestModel())
    assert isinstance(info, CityInfo)
    assert info.population_millions >= 0  # Field(ge=0) 制約 / constraint holds
