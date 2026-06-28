# Lesson 03 — ツールと依存性注入 / Tools & Dependency Injection

## 学ぶこと / What you'll learn
- ツール（関数）でエージェントに「行動」させる / Give the agent actions via tools
- `RunContext` 経由で**依存（deps）**にアクセスする / Reach deps via `RunContext`
- `deps_type` と `run_sync(..., deps=...)` の使い方 / `deps_type` and injecting deps
- ツールを単体テストする方法 / How to unit-test a tool

## 前提モジュール / Prerequisites
[Lesson 02](../02-structured-output/README.md)

## 手順 / Steps
```bash
make test
make run FILE=lessons/03-tools-and-deps/tools_and_deps.py
```

## ポイント解説 / Key points
- ツールは**普通の Python 関数**。第 1 引数が `RunContext[Deps]` だと、実行時に
  注入した依存へ `ctx.deps` でアクセスできます。`tools=[...]` に渡すだけで登録。
  A tool is a plain function; if its first arg is `RunContext[Deps]` it reaches
  injected deps via `ctx.deps`. Register by passing it to `tools=[...]`.
- **DI（依存性注入）の利点**: DB クライアントや API クライアントを `deps` として
  外から渡せるので、テストではフェイクに差し替えられます。モデル（`TestModel` /
  `FunctionModel`）と deps の両方を注入できることが、堅いテストの鍵です。
  DI lets you pass real clients in production and fakes in tests. Injecting both
  the model and the deps is the key to robust tests.
- ツール設計のベストプラクティス（命名・トークン効率・最小権限）は
  [`docs/concepts.md`](../../docs/concepts.md) を参照。
  See [`docs/concepts.md`](../../docs/concepts.md) for tool-design best practices.

## 演習 / Exercise
1. `humidity`（湿度）を返す 2 つ目のツールを追加する / Add a second tool for humidity.
2. `WeatherDeps` に「API クライアント」フィールドを足し、フェイクを注入してテストする。
   Add an API-client field to `WeatherDeps` and inject a fake in a test.
