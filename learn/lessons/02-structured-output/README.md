# Lesson 02 — 構造化出力 / Structured Output

## 学ぶこと / What you'll learn
- `output_type` に Pydantic モデルを渡して型付き出力を得る / Typed output via `output_type`
- `Field(description=...)` がモデルへの指示になる / `Field` descriptions guide the model
- 検証失敗時の自動リトライ（self-correction）/ Automatic retry on validation failure
- `custom_output_args` で出力を固定してテストする / Pin output in tests

## 前提モジュール / Prerequisites
[Lesson 01](../01-first-agent/README.md)

## 手順 / Steps
```bash
make test
make run FILE=lessons/02-structured-output/structured_output.py
```

## ポイント解説 / Key points
- 返り値は **dict ではなく Pydantic インスタンス**。`info.country` のように属性
  アクセスでき、型チェッカ（pyright/mypy）と IDE 補完が効きます。
  The result is a **Pydantic instance, not a dict** — attribute access with full
  type-checker and IDE support.
- `Field(ge=0, description=...)` の制約と説明は、(1) モデルへのヒント、(2) 返答の
  バリデーションの両方に効きます。検証に失敗すると Pydantic AI は失敗内容を添えて
  モデルに再生成を促します（`Agent(..., retries=N)` で回数調整）。
  Constraints/descriptions act as both model hints and response validation. On
  failure Pydantic AI re-prompts the model with the error (tune via `retries=N`).

## 演習 / Exercise
1. `CityInfo` に `timezone: str` を追加してみる / Add a `timezone` field.
2. `population_millions` を `int` に変え、`describe_city` の挙動を観察する。
   Change the type and observe how validation/coercion behaves.
