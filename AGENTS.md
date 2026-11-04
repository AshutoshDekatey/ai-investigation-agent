# Development guidance

Use the existing checkout; no worktrees unless requested. Read docs/RUNBOOK.md and docs/EVIDENCE.md before making readiness claims. Python 3.11+, `uv sync --frozen --extra dev`, `uv run --frozen --extra dev pytest -q`.

v0.1 remains in original modules; v0.2 is investigation.platform and the payments CLI. Default v0.2 retrieval must use pretrained Sentence Transformers, never silently fall back to test embeddings. TEST_EMBEDDINGS=1 is explicit plumbing validation only; label all metrics accordingly. Preserve actual reports including failures and encoder identity. Do not claim semantic quality from test embeddings or LLM results from deterministic tests.

Never initiate financial transactions, use real bank/customer information, commit secrets or run paid API calls without explicit approval. Fictional policy approval and date filters must apply to both retrieval arms. No LLM may override authoritative records. Keep exact citations and fail closed when applicable evidence is unavailable. Use PostgreSQL checkpoints/reports for the standard workflow and validate real HTTP tools, not just function stubs.

Keep v0.1 history/version docs. New changes need relevant regression checks. Do not disable TLS verification to work around model download/network restrictions. PRs must distinguish verified tests, unverified model paths and current limitations; do not merge automatically.
