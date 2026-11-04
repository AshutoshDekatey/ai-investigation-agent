# v0.2 architecture

The simulator serves a packaged synthetic transaction/ledger snapshot over authenticated HTTP GET. The investigation API authenticates analysts before running a LangGraph. Intake validates identifiers and dates and redacts common secret/email/long-number patterns. Transaction and ledger nodes perform bounded tool calls, then an independent deterministic assessment detects finality, duplicates and conflicts. Retrieval uses the evidence-derived topic plus the analyst question; the topic is not a gold evaluation label. Recommendation generation requires applicable retrieved evidence, verification checks quote integrity and Pydantic output, unresolved cases route to reconciliation, and final reports persist.

The graph uses PostgreSQL LangGraph checkpoints in the standard deployment, SQLite only when DATABASE_URL is absent. All graph state consists of JSON-safe dictionaries. A failed run carries an investigation ID for checkpoint recovery. API endpoints serialize graph runs with a lock to protect shared synchronous clients; this deliberately trades throughput for simplicity. This is a single-process prototype, not a distributed job scheduler. Completed resume returns the existing checkpoint report rather than creating a new investigation.

Reports persist separately in PostgreSQL for easy retrieval. Qdrant persists embeddings and metadata; BM25 is rebuilt over eligible documents per query (bounded corpus, currently 27 chunks). Named Docker volumes survive stops. Index rebuilding is a developer-only operation and must not run concurrently with investigation traffic.

## Trust boundaries

Neither API accepts arbitrary tool names, URLs, SQL, financial actions or approval to execute a payment. Only developers configure BANK_URL, DATABASE_URL and QDRANT_URL. LLM summaries receive a synthetic report as untrusted data and cannot overwrite canonical fields; prose is advisory and unverified. No LLM is necessary for the decision path. Approval flags gate paid summaries, not financial actions. Banking tokens and analyst tokens have separate scope. All analyst identities share one local role; tenant-level authorization, token rotation and production identity integration are out of scope.

Logs include only investigation ID, outcome and policy IDs. Pydantic redaction is a basic safeguard, not a production DLP guarantee. Raw fictional evidence persists in reports/checkpoints. LangSmith's automatic graph instrumentation is optional and not validated here; never enable it on real data or secrets.

The active implementation lives in `investigation.platform`. The old v0.1 runtime has been retired; its history and version notes remain available.
