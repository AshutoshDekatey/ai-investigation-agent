## Problem and behavior
Upgrade the fictional payment investigation baseline into a service that calls a read-only bank simulator, reconciles transaction and ledger records, retrieves effective approved policies and returns a cited recommendation with mandatory human review. Preserves v0.1 and its Git history.

Adds FastAPI analyst authentication, a nine-node LangGraph with PostgreSQL checkpoints and report storage, bounded HTTP tools, policy metadata/chunking, default Sentence Transformers embeddings, Qdrant/BM25 hybrid search, Docker Compose, a 60-case benchmark, CLI, opt-in OpenAI-compatible advisory summaries, CI and detailed runbook/security/cost documentation.

## Verified
- 30 offline tests passed, including interrupted-checkpoint recovery, API authorization, effective-date filtering, adversarial retrieved instructions, read-only boundaries and paid-mode guards.
- Running uvicorn banking and investigation APIs, Qdrant 1.14.1 and PostgreSQL 17.4 exercised through real HTTP and persisted records.
- Separate CLI process reloaded a PostgreSQL checkpoint.
- Actual 60-case **test-encoder** evaluation: 60/60 expected outcome categories, 100% citation/version/source-record checks, zero tested unsafe-action violations. Natural-language Recall@5 0.8182, MRR 0.6136 across 55 scorable cases.
- Actual reports, all per-case rankings and limitations are committed in reports/ and docs/EVIDENCE.md.

## Not yet verified / limitations
- Hugging Face model download blocked by network policy (ProxyError; CONNECT probe 403). Learned embeddings are the application default but their retrieval quality is NOT verified. TEST_EMBEDDINGS=1 is explicitly labelled plumbing mode, uses a separate collection, and never silently substitutes for learned mode.
- No paid LLM calls or LangSmith cloud traces executed. Optional live summaries are advisory, not independently graded.
- Benchmark repeats 12 scenario templates; outcome accuracy is not production/generalization accuracy. Groundedness is a citation/source-record integrity proxy.
- Cross-encoder reranking and independent semantic judges are deferred pending learned retrieval measurements. Single-process API, role-level auth, bounded corpus and concise fictional policies are prototype limitations.

## Reproduce
Follow docs/RUNBOOK.md for exact service, ingestion, learned-model access, evaluation and cleanup commands. Allow approved model-host access, rerun learned ingestion/evaluation, and review those results before claiming semantic readiness. No merge or environment publication requested automatically.
