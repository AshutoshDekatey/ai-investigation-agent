# Setup

Use the [runbook](RUNBOOK.md) for exact commands. Python 3.11+; uv manages the committed lock; Docker Compose starts pinned Qdrant 1.14.1 and PostgreSQL 17.4. `uv sync --frozen --extra dev` installs FastAPI, Pydantic, LangGraph, both checkpoint drivers, Qdrant client, BM25, CPU torch and Sentence Transformers. Qdrant client is constrained to the matching server minor. FastAPI/AnyIO are constrained to a compatible release family.

Required variables: BANK_API_TOKEN (simulator/tool shared token), ANALYST_API_TOKEN (analyst endpoint role), DATABASE_URL, QDRANT_URL, BANK_URL. No token defaults are supplied. Local development may omit DATABASE_URL/QDRANT_URL to use persistent SQLite and embedded Qdrant; do not concurrently open embedded Qdrant from multiple processes. `.cache` and `.env` are ignored. Learned embedding cache is controlled by HF_HOME.

Optional: TEST_EMBEDDINGS=1 for explicitly labelled plumbing tests, OPENAI_API_KEY/LLM_BASE_URL for approved summaries, LangSmith credentials for approved optional tracing. OpenAI and LangSmith access are not needed for offline tests. Necessary network domains include Python/CPU-wheel registries, Docker registries and Hugging Face model/redirect destinations. Restricted Codex environments must allow model-host requests through environment settings; no proxy bypass or disabled TLS is supported.
