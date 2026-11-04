# Verified evidence for v0.2

Validated in Codex Cloud with Python 3.12, CPU torch and locked dependencies. Commands executed against this checkout; no paid LLM calls or real financial operations occurred.

- Before legacy retirement, the combined suite had **30 passing tests**. After removing the 12 legacy-only tests, the active platform suite has **18 passing tests**, including the 60-case benchmark. The installed `payments` CLI works and the legacy `investigate` executable is absent. TestClient emits timeout-argument deprecation warnings; its in-process transport is distinct from the separately tested real timeout exception path.
- Docker Compose: Qdrant 1.14.1 and PostgreSQL 17.4 actually started with persistent named volumes and loopback ports.
- Banking uvicorn service: actual authenticated transaction/ledger HTTP GETs executed during evaluations.
- Investigation uvicorn service: health and OpenAPI returned 200; unauthenticated investigation returned 401; authenticated conflict case returned 200 with uncertainty; persisted report read returned 200.
- A **new CLI process** resumed a completed PostgreSQL LangGraph checkpoint successfully. Automated tests additionally recover from an interrupted graph after a retrieval failure.
- Compile checks and Git whitespace checks passed. GitHub Actions definition is provided; its hosted execution is not claimed verified.

## Actual benchmark

[Full report](../reports/v0.2-test-encoder.json), [retrieval-only report](../reports/retrieval-test-encoder.json), [API smoke report](../reports/api-smoke.json).

**Encoder: `test-only-hash`. These are infrastructure/regression measurements, not learned semantic performance.** There are 60 cases based on 12 repeated templates; 55 have a relevant approved policy for retrieval scoring.

| Metric | Actual result |
|---|---:|
| Natural-language retrieval Recall@5 | 0.8182 |
| MRR | 0.6136 |
| Expected outcome category match | 60/60 |
| Citation text/version checks | 100% |
| Groundedness proxy (citation/source-record integrity) | 100% |
| Expected read-only tool coverage | 100% |
| Tested unsafe-action violations | 0 |
| Full evaluation mean latency | See report (machine-dependent) |
| Full evaluation p95 latency | See report (machine-dependent) |
| LLM tokens/cost | 0 / $0 API usage |

The report retains per-case rankings, tool events, expected/actual outcome and failures (none for categorical outcomes in this run). Retrieval missed the expected policy in 10 of 55 scorable cases; those misses are not hidden by the outcome score. The workflow supplements the analyst question with the evidence-derived topic, while independent retrieval evaluation does not. This explains why the two measurements differ.

## Unverified and deferred

- **Pretrained semantic retrieval:** adapter initialization was attempted and failed with ProxyError; a Hugging Face CONNECT probe returned 403. [Access evidence](../reports/learned-model-access.json). Default application mode still requires learned weights; there is no silent fallback. Enable approved model-host access and run learned ingestion/retrieval/full evaluation from the runbook before claiming semantic readiness.
- **Live LLM summaries and provider cost:** no calls executed. The compatible API adapter, usage accounting and opt-in guards are implemented but a real provider response is unverified.
- **LangSmith:** optional configuration is documented, no cloud tracing run or cloud-cost claim.
- **Reranking and independent semantic judging:** no measured benefit available, so no reranker or fabricated judge score is supplied.
- Prototype policies are concise and fixtures correlated. This is not production accuracy, banking compliance, comprehensive DLP, tenant isolation or completed analyst approvals.

Environment publication is separate from the user-authorized Git merge. See RUNBOOK.md for exact reproduction and the remaining learned/live verification commands.
