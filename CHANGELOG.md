# Changelog

## Unreleased
- Record a user-reported successful local OpenAI summary with provenance, actual token usage and an estimated cost of $0.0001599 at supplied prices; no new paid calls were made.
- Use `max_completion_tokens` for optional Chat Completions summaries, retaining a 400-token budget and zero automatic retries.
- Record selected provider error status/code/parameter/message with credential redaction instead of hiding the reason behind `BadRequestError`.
- Add mocked SDK and CLI diagnostic tests; no live model compatibility or paid calls are claimed.

## 0.2.0
- Promoted the platform as the sole active implementation; removed the v0.1 runtime, CLI, fixtures and tests while retaining release history.
- Added the payment platform API, read-only bank simulator, settlement assessment and authenticated analyst endpoints.
- Added validated versioned policy ingestion, learned-embedding default, Qdrant/BM25 hybrid retrieval and exact citations.
- Added PostgreSQL reports, durable LangGraph checkpoints, resume, bounded tool failures and human routing.
- Added a 60-case benchmark, actual infrastructure evaluation, Compose and detailed operations/security/cost documentation.
- Retained v0.1; test-only infrastructure metrics are explicitly separated from unverified learned-model and live-LLM paths.

## 0.1.0
- Added synthetic transaction lookup, fictional policies, SQLite vector retrieval, and a LangGraph investigation workflow.
- Added typed evidence, recommendations, uncertainty and mandatory human review.
- Added offline CLI, evaluation cases, automated tests and optional LLM summaries.
