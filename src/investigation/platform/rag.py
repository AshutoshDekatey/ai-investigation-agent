"""Approved, date-filtered document retrieval with real Qdrant and BM25."""
import hashlib
import re
import uuid
from datetime import date
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from qdrant_client import QdrantClient, models
from rank_bm25 import BM25Okapi
from investigation.store import load_data

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Immutable model revision; downloads are TLS verified by Hugging Face.
REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"

def tokens(text):
    return re.findall(r"[a-z]+", text.lower())

class LearnedEncoder:
    name = MODEL + "@" + REVISION
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(MODEL, revision=REVISION, device="cpu")
    def encode(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

class TestEncoder:
    """Explicit plumbing fixture, NEVER described as learned semantic retrieval."""
    name = "test-only-hash"
    def encode(self, texts):
        import numpy as np
        vectors = []
        for text in texts:
            v = np.zeros(256)
            for token in tokens(text):
                v[int(hashlib.sha256(token.encode()).hexdigest()[:8], 16) % 256] += 1
            norm = np.linalg.norm(v)
            vectors.append((v / norm if norm else v).tolist())
        return vectors


class Document(BaseModel):
    id: str
    title: str
    topic: str
    version: int = Field(ge=1)
    effective_from: date
    effective_to: date
    approved: bool
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_range(self):
        if self.effective_from >= self.effective_to:
            raise ValueError("Policy validity range must be nonempty")
        return self

def chunks(documents):
    result = []
    for raw in documents:
        doc = Document.model_validate(raw).model_dump(mode="json")
        # Bounded overlapping word windows, retaining complete citation text.
        words = doc["text"].split()
        for offset in range(0, len(words), 100):
            text = " ".join(words[offset:offset+120])
            result.append(dict(doc, chunk_id=f'{doc["id"]}:v{doc["version"]}:{offset}', text=text))
    return result

class HybridIndex:
    def __init__(self, path=".cache/qdrant", url=None, encoder=None, collection="payment_policies"):
        self.encoder = encoder or LearnedEncoder()
        if url:
            self.client = QdrantClient(url=url)
        else:
            Path(path).mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=path)
        # Separate collection for test embeddings to avoid contaminating real index.
        self.collection = collection + ("_test" if isinstance(self.encoder, TestEncoder) else "")

    def ingest(self, documents=None):
        docs = chunks(documents if documents is not None else load_data("platform_policies.json"))
        vectors = self.encoder.encode([d["topic"] + " " + d["title"] + " " + d["text"] for d in docs])
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
        self.client.create_collection(self.collection, vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE))
        self.client.upsert(self.collection, points=[models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL,d["chunk_id"])), vector=v, payload=dict(d, embedding_model=self.encoder.name)) for d,v in zip(docs,vectors,strict=True)], wait=True)
        return len(docs)

    def search(self, query, as_of, k=5):
        # Validate model identity and filter both ranking arms identically.
        points, offset = self.client.scroll(self.collection, limit=1000, with_payload=True)
        if offset is not None:
            raise ValueError("Corpus exceeds v0.2 bounded index capacity")
        if any(p.payload.get("embedding_model") != self.encoder.name for p in points):
            raise ValueError("Embedding model mismatch: rebuild the index")
        eligible = [p for p in points if p.payload["approved"] and p.payload["effective_from"] <= str(as_of) < p.payload["effective_to"]]
        if not eligible:
            return []
        # Qdrant filtering restricts candidate IDs; expired/unapproved text never reaches model context.
        condition = models.Filter(must=[models.HasIdCondition(has_id=[p.id for p in eligible])])
        vector = self.client.query_points(self.collection, query=self.encoder.encode([query])[0], query_filter=condition, limit=max(k*3,10)).points
        bm25 = BM25Okapi([tokens(p.payload["topic"] + " " + p.payload["title"] + " " + p.payload["text"]) for p in eligible])
        scores = bm25.get_scores(tokens(query))
        lexical = [p for _,p in sorted(zip(scores,eligible),key=lambda pair: (-pair[0],str(pair[1].id)))][:max(k*3,10)]
        fused = {}
        for ranking in (vector, lexical):
            for rank, p in enumerate(ranking,1):
                fused[p.id] = fused.get(p.id,0) + 1/(60+rank)
        lookup = {p.id:p.payload for p in eligible}
        return [lookup[pid] for pid in sorted(fused,key=lambda pid:(-fused[pid],str(pid)))[:k]]

    def close(self):
        self.client.close()
