# Development guidance
Use the existing checkout; do not create worktrees unless requested. Use Python 3.11+ and `uv sync --frozen --extra dev`, then `uv run --frozen --extra dev pytest -q`.
Keep default execution offline and deterministic. Never initiate financial transactions. All datasets and policies must be clearly synthetic/fictional. Do not commit secrets or make paid API calls without user approval. Real LLM and model-download checks are optional and must be reported separately from offline verification. Preserve structured evidence and fail closed when policy evidence is absent.
