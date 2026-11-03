"""SQLite vector search with deterministic offline concept embeddings.

This small synonym encoder is transparent, not a pretrained language model.
Use SentenceEmbeddings for learned semantic embeddings (optional download).
"""
import hashlib
import re
import sqlite3
import numpy as np
from .models import Policy

class ConceptEmbeddings:
    dimension = 256
    concepts = {
        "completed": "settled", "successful": "settled", "success": "settled",
        "declined": "failed", "rejected": "failed", "failure": "failed",
        "processing": "unresolved", "pending": "unresolved", "unknown": "unresolved",
        "missing": "unresolved", "uncertain": "unresolved",
    }

    def encode(self, texts):
        result = []
        for text in texts:
            vector = np.zeros(self.dimension, dtype=np.float32)
            for token in re.findall(r"[a-z]+", text.lower()):
                token = self.concepts.get(token, token)
                index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % self.dimension
                vector[index] += 1
            norm = np.linalg.norm(vector)
            result.append(vector / norm if norm else vector)
        return np.asarray(result)

class SentenceEmbeddings:
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def encode(self, texts):
        return self.model.encode(texts, normalize_embeddings=True)

class PolicyIndex:
    def __init__(self, policies: list[Policy], encoder=None):
        self.encoder = encoder or ConceptEmbeddings()
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE policies (id TEXT PRIMARY KEY, document TEXT, vector BLOB)")
        vectors = self.encoder.encode([p.title + " " + p.text for p in policies])
        for p, v in zip(policies, vectors, strict=True):
            self.db.execute("INSERT INTO policies VALUES (?, ?, ?)", (p.id, p.model_dump_json(), np.asarray(v, dtype=np.float32).tobytes()))

    def search(self, query: str, k: int = 3) -> list[Policy]:
        if k < 1:
            raise ValueError("k must be positive")
        q = np.asarray(self.encoder.encode([query])[0], dtype=np.float32)
        scored = [(float(np.dot(q, np.frombuffer(v, dtype=np.float32))), pid, doc)
                  for pid, doc, v in self.db.execute("SELECT id, document, vector FROM policies")]
        return [Policy.model_validate_json(doc) for _, _, doc in sorted(scored, key=lambda x: (-x[0], x[1]))[:k]]

    def close(self):
        self.db.close()
