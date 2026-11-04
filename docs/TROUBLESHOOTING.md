# Troubleshooting

- 401: verify the correct shared simulator token or analyst bearer token is set in the appropriate processes; never log its value.
- 503 from investigation: inspect the returned checkpoint ID, verify the model cache, policy collection, bank API and database. Repair then resume; do not fabricate a report.
- Qdrant collection missing: run ingestion with the same encoder mode/server URL. An encoder mismatch requires rebuilding the dedicated collection.
- Qdrant local storage locked: embedded mode allows one process; use Qdrant server for CLI plus API.
- Hugging Face ProxyError/403: network policy must permit the model-host and download redirects. Do not disable certificate or artifact verification. Test-only mode does not resolve learned-model readiness.
- Docker unavailable: inspect the managed daemon/socket in Codex; no second daemon or host networking workaround. On WSL, ensure Docker Desktop WSL integration is enabled.
- PostgreSQL password failure: an initialized volume keeps its original credentials. Reuse the original secure configuration; only delete volumes if intentionally discarding synthetic data.
- uv cache read-only: export UV_CACHE_DIR=/tmp/uv-cache in Codex, then rerun.
- TestClient hangs in restricted Codex command sandbox: run tests with local-network permission. Do not leave timed-out tests running.
- Git push works but gh PR creation says Forbidden: GitHub API access differs from Git proxy access; allow api.github.com in environment settings, or open a PR through the comparison link. Never request/extract proxy-held credentials.
- Live provider error: check endpoint, model availability and structured JSON support; record error types, not secrets or raw credential-bearing exception text. Paid failures can still incur costs.
