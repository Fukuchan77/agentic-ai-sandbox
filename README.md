# agentic-ai-sandbox 🤖

**IBM × Anthropic 公式準拠で、AI Agents / Agentic AI を「基礎 → パターン → 応用 → 本番 → ガバナンス」まで
一本で学べるモノレポ。**
**A single monorepo for learning Agentic AI / AI agents end-to-end — fundamentals → patterns →
applications → production → governance — aligned with official IBM & Anthropic guidance.**

> ## 👉 入口はここ / Start here: [`docs/learning-path.md`](docs/learning-path.md)
> Stage 0–5 を貫く**唯一の学習パス**です。まずこのページを読んでください。
> The single learning path across Stages 0–5 — read this first.

---

## 2 つのティア / Two tiers

このリポジトリは、学習の段階に応じて **2 つのティア**に分かれています（同一リポ内・相対リンクで地続き）。

| ティア / Tier | Stage | 役割 / Role | ゲート / Gates | 入口 / Entry |
|---|---|---|---|---|
| **[`learn/`](learn/README.md)** | 0–3 | 学ぶ（12 レッスン＋フレームワーク比較トラック）| 緩い（オフライン pytest、API キー不要）| [`learn/README.md`](learn/README.md) |
| **[`reference/`](reference/README.md)** | 4–5 | 参照・本番・ガバナンス（FastAPI 本体＋`patterns/`＋SDD specs）| 厳格（pyright strict / cov98 / 契約ドリフト）| [`reference/README.md`](reference/README.md) |

```
agentic-ai-sandbox/
├── docs/         # ★ 全 Stage 横断の地図（learning-path = 単一入口）
├── learn/        # Stage 0–3：レッスン + frameworks/（緩いゲート）
└── reference/    # Stage 4–5：app/（FastAPI）+ patterns/ + specs/（厳格ゲート）
```

---

## クイックスタート / Quick start

ツールは **[mise](https://mise.jdx.dev/)** に一本化しています（`mise install` で Python 3.13＋uv を取得）。
mise 未導入でも各ティアの README に `uv run` 直叩きの等価コマンドを併記しています。

```bash
mise install                 # Python 3.13 + uv を用意 / provision toolchain

# 学ぶ（Stage 0–3、オフライン・API キー不要）
mise run learn:test          # = cd learn && uv run pytest

# 参照/本番（Stage 4、厳格ゲート）
mise run reference:check     # lint / format / pyright(strict) / pytest
mise run patterns:check      # patterns/ 各レーンの厳格ゲート

mise run check               # 全ティア集約（CI と同じ）/ aggregate across all tiers
```

タスク一覧は [`mise.toml`](mise.toml) を参照（`learn:*` / `reference:*` / `patterns:*`）。

---

## ドキュメント地図 / Docs map

すべて **同一リポ内の相対リンク**です（クロスリポ URL は撤廃済み）。

| ファイル / File | 内容 / What |
|---|---|
| [`docs/learning-path.md`](docs/learning-path.md) | ★ 単一入口。Stage 0–5 の全体像と公式ソース対応表 |
| [`docs/roadmap.md`](docs/roadmap.md) | Stage 1–3 のレッスン順 |
| [`docs/agent-types.md`](docs/agent-types.md) ・ [`docs/concepts.md`](docs/concepts.md) | Stage 0：型 / generative vs agentic / 自律性・設計思想 |
| [`docs/framework-comparison.md`](docs/framework-comparison.md) | learn の framework トラック設計差 |
| [`docs/provider-setup.md`](docs/provider-setup.md) | Anthropic / Ollama 切替 |
| [`docs/tool-design.md`](docs/tool-design.md) ・ [`docs/context-engineering.md`](docs/context-engineering.md) | Anthropic「ツール設計」「文脈設計」の解説 |
| [`docs/governance-and-scale.md`](docs/governance-and-scale.md) | ★ Stage 5：identity / scale / deploy / OWASP |

---

## CI

`.github/workflows/` は path フィルタでティア／レーン別に分かれ、Python は全て 3.13 です：
`learn-ci`（`learn/**`）・`reference-ci`（`reference/app/**`）・`patterns-ci`（`reference/patterns/**`）
＋ live integration / security。ドキュメントの相対リンク健全性は
[`scripts/check_doc_links.py`](scripts/check_doc_links.py) が検査します。

## ライセンス / License

MIT — [`LICENSE`](LICENSE)
