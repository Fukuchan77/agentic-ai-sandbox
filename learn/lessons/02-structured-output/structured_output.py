"""Lesson 02 — 構造化出力 / Structured output.

LLM の自由テキストは扱いにくい。Pydantic AI では ``output_type`` に Pydantic
モデルを渡すだけで、**検証済みの型付きオブジェクト**が返ります。検証に失敗すると
Pydantic AI が自動でモデルに再試行を促します（self-correction）。

Free-form text is hard to consume. With Pydantic AI you pass a Pydantic model
to ``output_type`` and get back a **validated, typed object**. If validation
fails, Pydantic AI automatically asks the model to retry (self-correction).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from bootcamp_common.provider import get_model

if TYPE_CHECKING:
    from pydantic_ai.models import Model


class CityInfo(BaseModel):
    """都市の基本情報 / Basic facts about a city."""

    name: str = Field(description="都市名 / city name")
    country: str = Field(description="国名 / country")
    population_millions: float = Field(
        ge=0,
        description="人口（百万人単位）/ population in millions",
    )
    famous_for: list[str] = Field(
        description="有名なもの 2〜4 個 / 2-4 things it is famous for",
    )


def build_agent(model: Model | None = None) -> Agent[None, CityInfo]:
    """``CityInfo`` を返すエージェント / An agent that returns ``CityInfo``."""
    return Agent(
        model=model or get_model(),
        output_type=CityInfo,  # ← これだけで型付き出力 / typed output, just this
        instructions="ユーザーが挙げた都市について、簡潔な事実を埋めてください。",
    )


def describe_city(city: str, model: Model | None = None) -> CityInfo:
    return build_agent(model).run_sync(city).output


def main() -> None:
    info = describe_city("京都")
    # info は dict ではなく CityInfo インスタンス。属性アクセスでき、IDE 補完も効く。
    # info is a CityInfo instance (not a dict): attribute access + IDE completion.
    print(f"{info.name}, {info.country} — {info.population_millions}M")
    print("famous for:", ", ".join(info.famous_for))


if __name__ == "__main__":
    main()
