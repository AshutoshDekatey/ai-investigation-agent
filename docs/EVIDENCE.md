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

## User-reported local live test — 2026-11-04

The user supplied terminal output from a successful local WSL `live-eval --limit 1` run after the completion-budget compatibility fix. [Recorded output and provenance](../reports/live-summary-user-reported.json). This was not independently rerun in Codex.

- Reported model: `gpt-6-luna`; transaction: `SIM-001`.
- Input: **824 tokens**; completion: **155 tokens**; total: **979 tokens**.
- Completion includes 44 reasoning tokens; these must not be counted twice.
- Estimated cost: **$0.0001599**, using user-supplied rates of $0.10 input / $0.50 output per million tokens. Provider billing was not independently verified.
- The returned summary distinguished recorded settlement from merchant receipt and retained the human-review requirement. `advisory_unverified: true` labels the prose; it is not a failed-call flag.
- The user also reported downloading pretrained Sentence Transformers weights locally. No learned-retrieval evaluation metrics were supplied.

This establishes one user-reported successful live summary, not production accuracy, independent semantic judgment or a multi-case LLM benchmark. No credentials were supplied or committed, and no additional paid calls were made for this documentation update.

## Unverified and deferred

- **Pretrained semantic retrieval:** adapter initialization was attempted and failed with ProxyError; a Hugging Face CONNECT probe returned 403. [Access evidence](../reports/learned-model-access.json). Default application mode still requires learned weights; there is no silent fallback. Enable approved model-host access and run learned ingestion/retrieval/full evaluation from the runbook before claiming semantic readiness.
- **Broader live LLM accuracy and billing:** one successful local summary is user-reported above; multi-case accuracy, independent judging and provider billing remain unverified.
- **LangSmith:** optional configuration is documented, no cloud tracing run or cloud-cost claim.
- **Reranking and independent semantic judging:** no measured benefit available, so no reranker or fabricated judge score is supplied.
- Prototype policies are concise and fixtures correlated. This is not production accuracy, banking compliance, comprehensive DLP, tenant isolation or completed analyst approvals.

Environment publication is separate from the user-authorized Git merge. See RUNBOOK.md for exact reproduction and the remaining learned/live verification commands.

## Subsequent LLM compatibility fix

The compatibility branch has **21 passing offline tests**, including mocked SDK request/usage validation, provider diagnostic redaction and one-case CLI failure handling without retries. The request now uses `max_completion_tokens=400`. The original generic BadRequestError did not identify its cause. The user subsequently reported one successful live summary after this fix, as recorded above. No additional paid calls were made by Codex.
