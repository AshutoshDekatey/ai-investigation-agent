# Architecture

`CLI -> LangGraph: lookup -> retrieve -> assess -> structured JSON`

The lookup node reads an immutable Pydantic transaction from a packaged synthetic snapshot. It has no network or payment execution interface. Retrieval embeds the recorded status query and fictional policy documents, stores float32 vectors in an ephemeral SQLite database, and ranks by cosine similarity. The offline encoder hashes normalized words and a small explicit synonym vocabulary into 256 dimensions. It demonstrates concept matching, not general natural-language understanding; collisions and vocabulary gaps are possible. Optional MiniLM sentence-transformer embeddings provide learned semantics and require a model download.

All three tiny policies are retrieved in v0.1 so a deterministic status rule can select applicable evidence. Retrieval ranking is tested independently; this is deliberately not a scalable retrieval benchmark. Missing applicable policy causes manual escalation. All outcomes retain uncertainty and require human review. Settled describes the snapshot state, not independently verified beneficiary receipt.

Optional OpenAI structured output summarizes the deterministic report. It cannot change authoritative fields; its prose remains unverified advisory text. Errors retain the offline result and add uncertainty. No dispute narrative is accepted in v0.1, no tools are exposed to the LLM, and no action executor exists. This is decision support, not automated banking adjudication.

Data lives in `src/investigation/data`; evaluation expectations live in `evals/cases.json`. The SQLite index is rebuilt per CLI process. No accounts, PII or credentials are stored.
