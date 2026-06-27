# プロバイダ設定 / Provider Setup

このコースは `LLM_PROVIDER` 環境変数 1 つで **Anthropic** と **Ollama** を切り替えます。
コードは一切変えません（`bootcamp_common/provider.py` が吸収）。
Switch between **Anthropic** and **Ollama** with the single `LLM_PROVIDER` env var —
no code changes (handled by `bootcamp_common/provider.py`).

> 💡 学習・テストだけなら**どちらも不要**です。すべてのテストは `TestModel` /
> `FunctionModel` で動くので、`make test` は API キーなしで通ります。
> For learning/testing you need **neither** — `make test` passes with no API key.

---

## 共通の準備 / Common setup

```bash
make setup            # uv sync
cp .env.example .env  # 値を編集 / edit values
```

---

## A. Anthropic（既定 / default, 推奨 / recommended）

最新の Claude を使うため、品質が高く Pydantic AI との相性も良い構成です。
Uses the latest Claude — highest quality and great Pydantic AI integration.

1. [console.anthropic.com](https://console.anthropic.com/) で API キーを発行 / create a key.
2. `.env` を編集 / edit `.env`:
   ```dotenv
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_MODEL=claude-sonnet-4-6
   ```

### モデルの選び方 / Choosing a model
| モデル / Model | 用途 / Use |
|---|---|
| `claude-haiku-4-5` | 低コスト・高速。学習中はこれで十分 / cheap & fast — ideal while learning |
| `claude-sonnet-4-6` | バランス型・既定 / balanced default |
| `claude-opus-4-8` | 最難タスク向け / for the hardest tasks |

> モデル ID はコードにハードコードせず `.env` に置きます（差し替えを容易にするため）。
> Model IDs live in `.env`, never hardcoded — so they're easy to swap.

---

## B. Ollama（ローカル・無償 / local, free）

API コストをかけずに試したいときに。An option to experiment without API cost.

1. [ollama.com](https://ollama.com/) をインストール / install Ollama.
2. デーモンを起動し、モデルを取得 / start the daemon and pull a model:
   ```bash
   ollama serve &
   ollama pull llama3.2
   ```
3. `.env` を編集 / edit `.env`:
   ```dotenv
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434/v1   # 末尾 /v1 が必須 / trailing /v1 required
   OLLAMA_MODEL=llama3.2
   ```

> ⚠️ 小さなローカルモデルは、構造化出力（lesson 02）やツール呼び出し（lesson 03）で
> Claude ほど安定しないことがあります。挙動の確認には十分ですが、品質差は理解しておきましょう。
> Small local models can be less reliable at structured output / tool calling than
> Claude. Fine for seeing behavior, but expect a quality gap.

---

## 動作確認 / Verify

```bash
# オフライン（キー不要）/ offline, no key:
make test

# 実プロバイダで 1 回 / one real call:
make run FILE=lessons/00-setup/hello_agent.py
```

`get_model()` は構築時にネットワークを使いません。実際の通信は `agent.run(...)` まで
遅延されるので、設定ミスは最初の実行で分かります。
`get_model()` does no network I/O at construction; the first `agent.run(...)` is
where misconfiguration surfaces.
