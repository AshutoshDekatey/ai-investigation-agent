# Beginner runbook (WSL/Linux)

All records, credentials generated below, and policies belong to a fictional local simulator. Do not substitute real customer data. Run commands from the repository root. Keep terminal 1's environment exported; repeat the exports in each new terminal. Do not commit `.env` files or shell secrets.

## 1. Clone the implementation

```sh
git clone https://github.com/AshutoshDekatey/ai-investigation-agent.git
cd ai-investigation-agent
git switch feat/payment-platform-v0.2
```

After the upgrade is merged, use `main` instead. Existing checkouts: `git fetch origin` before switching branches; preserve your local changes.

## 2. Python and dependencies

Install Python 3.11+ and uv using their official installers and install Docker Engine with the Compose plugin (or Docker Desktop with WSL integration). Verify:

```sh
python3 --version
uv --version
docker compose version
uv sync --frozen --extra dev
export HF_HOME="$PWD/.cache/huggingface"
export UV_CACHE_DIR="$PWD/.cache/uv"
```

The lock selects CPU-only torch. The Python wheels/model download can take several minutes. Later invocations reuse them.

## 3. Start persistent Qdrant and PostgreSQL

```sh
export POSTGRES_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
export BANK_API_TOKEN=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
export ANALYST_API_TOKEN=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
export DATABASE_URL="postgresql://investigation:${POSTGRES_PASSWORD}@127.0.0.1:5432/investigation"
export QDRANT_URL=http://127.0.0.1:6333
export BANK_URL=http://127.0.0.1:8001
docker compose up -d
docker compose ps
docker compose exec postgres pg_isready -U investigation
curl --fail http://127.0.0.1:6333/healthz
```

Wait until PostgreSQL accepts connections. Named volumes survive container stops. Changing the password export does not change an already initialized database; retain your local environment securely. Loopback ports are deliberate; do not expose these unauthenticated databases publicly.

## 4. Start simulated banking API

In terminal 1, with `BANK_API_TOKEN` exported:

```sh
uv run --frozen uvicorn investigation.platform.bank:app --host 127.0.0.1 --port 8001
```

Leave it running. A second terminal needs the same environment variables (store them securely locally or export them through your environment manager). Do not paste tokens into chat.

```sh
curl --fail http://127.0.0.1:8001/health
curl --fail -H "X-Bank-Token: $BANK_API_TOKEN" http://127.0.0.1:8001/transactions/SIM-001
```

## 5–6. Ingest documents, embed, and index

```sh
uv run --frozen payments ingest
```

This validates `src/investigation/data/platform_policies.json`, extracts metadata, creates overlapping 120-word chunks with a 100-word stride, downloads pinned MiniLM weights, embeds text and metadata on CPU, and upserts Qdrant points. It **rebuilds the dedicated policy collection**; do not run ingestion concurrently with investigations. Ingesting a trusted alternative corpus: `payments ingest --documents path/to/policies.json` (same schema). Never mark untrusted attachments approved without analyst governance.

## 7. Retrieval evaluation

```sh
uv run --frozen payments retrieve-eval --output reports/retrieval-learned.json
```

This uses natural-language benchmark questions, not gold labels. Inspect Recall@5, MRR, per-case rankings and misses. Do not substitute test-encoder metrics for learned retrieval results.

## 8. Start investigation service

With all exports available in terminal 2:

```sh
uv run --frozen uvicorn investigation.platform.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` locally for OpenAPI. `/health` is process liveness, not a readiness test for all dependencies. An investigation is the functional readiness check.

## 9. Investigate a payment

In a third terminal with the same environment:

```sh
uv run --frozen payments investigate SIM-001
curl --fail -H "Authorization: Bearer $ANALYST_API_TOKEN" -H 'Content-Type: application/json' \
  -d '{"transaction_id":"SIM-006","question":"Debited but merchant did not receive it","as_of":"2026-11-04"}' \
  http://127.0.0.1:8000/investigations
```

SIM-001 success, SIM-002 failure, SIM-003 pending, SIM-005 duplicate, SIM-006 conflict, SIM-007 missing, SIM-008 incomplete, SIM-011 unavailable bank. These are synthetic snapshot records. The default as-of date is fixed to the fictional benchmark date; pass another date through the API when evaluating policy versions.

## 10. Inspect evidence and recovery

Reports contain `investigation_id`, `transaction_id`, `outcome`, `records`, `tool_events`, `retrieved`, `citations`, `recommendation`, `uncertainty`, `route`, `human_review`, `embedding_mode`, `latency_ms`, `llm`. Citation entries have `chunk_id`, `policy_id`, `version`, `quote`, `source` (a `policy://` identifier resolving to the packaged policy corpus).

```sh
export INVESTIGATION_ID=replace-with-report-id
curl --fail -H "Authorization: Bearer $ANALYST_API_TOKEN" "http://127.0.0.1:8000/investigations/$INVESTIGATION_ID"
uv run --frozen payments resume "$INVESTIGATION_ID"
```

A failed API run returns its checkpoint ID in the 503 detail. Repair the dependency, then call the authenticated `POST /investigations/{id}/resume` endpoint or CLI. This recovers graph execution, not any financial operation. Reports in PostgreSQL and graph checkpoint tables survive process restarts. Operations logs include only bounded synthetic IDs/outcomes/policy IDs. Full synthetic evidence is in persisted reports.

## 11. Complete free/offline evaluation

After the model is cached, use `HF_HUB_OFFLINE=1` to ensure no model download. No LLM key is needed:

```sh
uv run --frozen --extra dev pytest -q
HF_HUB_OFFLINE=1 uv run --frozen payments evaluate --output reports/full-learned.json
```

For **test plumbing only**, explicitly `export TEST_EMBEDDINGS=1`, then rerun ingestion and evaluation. It uses a separate `_test` collection. This mode is not genuine semantic evaluation. `unset TEST_EMBEDDINGS` restores learned embeddings; ingest again if needed. Unit tests always select test embeddings in isolated temporary storage, not via a hidden application fallback.

## 12. Optional paid LLM configuration and estimate

Obtain separate API approval first. ChatGPT subscriptions do not cover API charges. Securely export `OPENAI_API_KEY`; optionally set `LLM_BASE_URL` for an OpenAI-compatible endpoint. No key belongs in Git. See COSTS.md for input/output estimation and failure accounting. LangSmith tracing is optional: set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT` securely; trace synthetic inputs only. Cloud tracing may incur separate costs and was not enabled during validation.

## 13. Small live evaluation (only after approval)

First estimate with actual provider prices: at most 10 reports × roughly 8,000 input tokens + 400 output tokens per report. Rates below are placeholders to replace with current USD/million prices, not an approval or known model price:

```sh
# ONLY after cost approval; set current provider rates first.
export INPUT_RATE=replace-with-current-numeric-rate
export OUTPUT_RATE=replace-with-current-numeric-rate
uv run --frozen payments live-eval --limit 10 --model gpt-4.1-mini --allow-paid-api \
  --input-usd-per-million "$INPUT_RATE" --output-usd-per-million "$OUTPUT_RATE" \
  --output reports/live-10.json
```

The command limits runs to 1–20 cases, no automatic provider retries, and 400 output tokens per call. Returned usage determines estimated cost; failed calls may still be billed, so reconcile with provider billing. This summary demo is not a judged real-LLM recommendation benchmark.

## 14. Examine metrics/traces

```sh
python3 -m json.tool reports/full-learned.json
```

Review `failures`, per-case expected/actual outcomes, tool events, retrieval ranks and encoder identity. Inspect model usage/cost fields in live reports. Without LangSmith, PostgreSQL checkpoints and structured logs provide local execution history; retrieved snippets and tool decisions are in reports.

## 15. Stop and clean up

Stop uvicorn terminals with Ctrl-C, then:

```sh
docker compose stop
# To remove containers while retaining data:
docker compose down
# DESTRUCTIVE: only if you want to delete synthetic DB/vector volumes:
docker compose down -v
```

Temporary local `.cache` stores may be removed only after stopping all processes using them; retain the model cache if avoiding a redownload.

## Codex Cloud

Use the existing checkout, no new worktree. Use a writable `UV_CACHE_DIR=/tmp/uv-cache`. Local servers/tests may need command network permission. Check the managed Docker daemon; do not start a second daemon or bypass its proxy. Hugging Face was blocked by the network policy in this session. Add `huggingface.co` and any model-download redirect hosts identified by a policy diagnostic to environment settings, then retry learned ingestion; never disable TLS verification. GitHub PR API needs `api.github.com` access. Do not expose localhost as a public preview. `TEST_EMBEDDINGS=1` permits infrastructure validation while the model access is unavailable, but does not complete learned-model validation. Publish/snapshot configuration is separate and not performed by this project.
