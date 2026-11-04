## Problem and behavior
Disputed payments need recommendations grounded in recorded transaction status and policy evidence. This v0.1 adds a read-only synthetic payment lookup, fictional policies, SQLite vector retrieval, and a LangGraph workflow producing Pydantic-validated evidence, recommendations, uncertainty and mandatory human review.

Includes an offline CLI, deterministic concept embeddings, optional sentence-transformer embeddings, opt-in OpenAI structured summaries, a uv lockfile, CI, five evaluation cases and architecture/version documentation. LLM summaries cannot change deterministic report fields. No payment execution capability exists.

## Validation
- `UV_CACHE_DIR=/tmp/uv-cache uv run --frozen --extra dev pytest -q`: 12 passed.
- `investigate PAY-001`: verified structured report with transaction and policy evidence.
- Tests cover settled, failed, pending, unknown and missing payments; retrieval ranking; immutable records; missing-policy escalation; fake LLM success/failure; CLI JSON and paid-mode guard.

## Limits
Policies and records are fictional. Offline embeddings use explicit synonyms and hashed tokens, not a learned encoder; the tiny index retrieves all three policies before deterministic evidence selection. Real OpenAI execution and optional sentence-transformer downloads were not run. No paid API calls were made. This is a decision-support demo, not production banking adjudication.
