# AI Investigation Agent — v0.1

Read-only investigation of disputed **synthetic** banking payments using recorded transaction state and **fictional** policies. Produces evidence-based decision support with uncertainty and mandatory human review. Never sends payments, refunds or retries.

## Quick start

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are required.

```sh
uv sync --frozen --extra dev
uv run --frozen investigate PAY-001
uv run --frozen investigate PAY-002
uv run --frozen investigate PAY-003
uv run --frozen --extra dev pytest -q
```

IDs: PAY-001 settled, PAY-002 failed, PAY-003 pending, PAY-004 unknown; other IDs return a missing-record escalation. JSON includes `status`, `evidence`, `policy_ids`, `recommendation`, `uncertainty`, `human_review`, `mode` and optional `llm_summary`. Amounts are decimal strings. The snapshot is historical synthetic data, never a live balance or current payment status.

## Retrieval and orchestration

LangGraph runs lookup → retrieval → assessment. Pydantic validates records and reports. SQLite holds embedded policy vectors. Default embeddings normalize a small synonym vocabulary and hash tokens for fully offline, deterministic concept retrieval. This is a limited semantic baseline, not a pretrained encoder. See [architecture](docs/architecture.md) and [v0.1 scope](docs/versions/v0.1.md).

For optional learned embeddings (downloads model weights; not exercised by offline tests):

```sh
uv sync --extra semantic --extra dev
uv run investigate PAY-001 --embeddings sentence-transformers
```

## Optional real LLM mode

Default mode makes no API calls. After separately approving costs, set `OPENAI_API_KEY` securely in your shell/environment settings, then explicitly opt in:

```sh
uv run investigate PAY-001 --llm --allow-paid-api --model gpt-4.1-mini
```

Uses the OpenAI Responses API with Pydantic structured summaries. Only synthetic evidence is sent to the API. Model availability depends on your account. The LLM cannot override deterministic decisions; summaries are advisory. Failure adds uncertainty and retains the offline assessment. Never commit API keys. Real API execution and optional model downloads are not claimed as verified by the offline test suite.

## Evaluation

`evals/cases.json` covers successful, failed, pending, unknown and missing transactions. Pytest checks expected policy evidence and recommendations, deterministic repeatability, synonym retrieval, read-only records, policy-missing escalation, fake LLM paths, CLI output and paid-mode opt-in. CI runs the locked offline suite. These fixtures demonstrate behavior, not production accuracy.
