# AI Payments Investigation & Decision Support — v0.2

A fictional banking analyst investigates “money was debited but the merchant did not receive it.” The platform calls a running read-only simulated bank API, compares transaction and settlement evidence, retrieves dated payment policies, and returns a cited recommendation with uncertainty and mandatory human review.

**No real bank connections, customer data, or financial execution tools exist.** This is a portfolio prototype, not a production adjudication service.

## Start here

Follow the copy-paste [runbook](docs/RUNBOOK.md). Requires Python 3.11+, uv, Docker Compose and about 2 GB for CPU dependencies/model weights. First embedding-model download needs Internet access; after caching, the deterministic investigation workflow requires no paid service.

```sh
uv sync --frozen --extra dev
uv run --frozen --extra dev pytest -q
```

Core command: `payments investigate SIM-001` after services and ingestion are prepared. `payments retrieve-eval` and `payments evaluate` save quantitative reports. The investigation FastAPI service exposes `/health`, `/docs`, `POST /investigations`, report lookup and checkpoint resume. Requests require an analyst bearer token. Model downloads are not LLM API calls.

## Implementation

- Sentence Transformers MiniLM learned embeddings by default, pinned model revision; Qdrant persistent vectors and BM25 combined through reciprocal-rank fusion.
- 24 current fictional policies, two historical versions, one unapproved adversarial attachment; validated metadata, date filtering, chunk-level exact citations.
- Nine LangGraph nodes: intake, transaction lookup, ledger lookup, assessment, retrieval, recommendation, verification, human routing, report persistence.
- Authenticated GET-only banking tools with timeouts, at most two attempts by default, validation and explicit evidence gaps.
- PostgreSQL reports and LangGraph checkpoints; SQLite and Qdrant embedded mode available for isolated development/tests.
- Separate opt-in OpenAI-compatible advisory summary integration, usage accounting and bounded live evaluation. A user-reported local run successfully produced one live summary; see the evidence below.

## Verified evidence and limits

See [actual reports](reports/v0.2-test-encoder.json) and [evidence](docs/EVIDENCE.md). The 60-case HTTP/Qdrant/PostgreSQL run uses the **explicit test-only encoder** because Codex network policy blocked Hugging Face. It verifies infrastructure and rules, **not learned semantic quality**. Production defaults never silently fall back to test embeddings. A subsequent user-reported local OpenAI run returned one successful advisory summary: 824 input + 155 output tokens, estimated $0.0001599 at supplied rates. See the [recorded live result](reports/live-summary-user-reported.json). Learned retrieval quality and broader LLM accuracy remain unverified.

The benchmark repeats 12 scenario templates five times; it is a regression set, not an independent production accuracy estimate. Human-review routing is implemented; analyst approval UI/execution is not. Cross-encoder reranking is deferred until learned retrieval measurements justify it. Full limitations are in [evaluation](docs/EVALUATION.md).

[Architecture](docs/ARCHITECTURE.md) · [setup](docs/SETUP.md) · [RAG design](docs/RAG_DESIGN.md) · [tests](docs/TESTING.md) · [costs](docs/COSTS.md) · [troubleshooting](docs/TROUBLESHOOTING.md) · [v0.2](docs/versions/v0.2.md)

The `payments` CLI is the sole active implementation. The legacy v0.1 runtime, fixtures and `investigate` command have been removed. Earlier releases remain documented in Git history and version notes.
