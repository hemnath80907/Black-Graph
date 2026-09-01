"""
Lightweight semantic retrieval layer.

Implements TF-IDF vectorization + cosine similarity from scratch (stdlib only)
so the RAG component has no hard dependency on an external embeddings API or
heavy ML library. This keeps the retrieval layer runnable even in an offline
/ degraded environment, and is swappable for a real embeddings-based vector
DB (e.g. FAISS, pgvector) without changing the calling contract:

    retriever.query(text, top_k=3) -> List[RetrievedChunk]
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


TOKEN_RE = re.compile(r"[a-zA-Z]{2,}")

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these", "those",
    "with", "as", "at", "by", "from", "it", "its", "we", "our", "they",
    "their", "has", "have", "had", "will", "would", "could", "should",
    "not", "no", "but", "if", "than", "then", "so", "such", "into", "over",
    "under", "up", "down", "out", "about", "which", "who", "what", "when",
    "where", "how", "may", "can", "do", "does", "did", "also",
}


def tokenize(text: str) -> List[str]:
    return [
        tok.lower()
        for tok in TOKEN_RE.findall(text)
        if tok.lower() not in STOPWORDS
    ]


@dataclass
class Document:
    doc_id: str
    source: str          # display name, e.g. "RELIANCE_annual_filing_2025.txt"
    symbol: str           # ticker this document primarily concerns
    chunk_id: int
    text: str


@dataclass
class RetrievedChunk:
    document: Document
    score: float


def _split_into_chunks(raw_text: str, chunk_size_lines: int = 6) -> List[str]:
    """Chunk a document into overlapping ~paragraph windows for retrieval."""
    lines = [ln for ln in raw_text.splitlines() if ln.strip()]
    chunks = []
    step = max(1, chunk_size_lines - 1)  # slight overlap
    for i in range(0, len(lines), step):
        window = lines[i:i + chunk_size_lines]
        if window:
            chunks.append(" ".join(window).strip())
    return chunks or [raw_text.strip()]


class TfidfVectorStore:
    """A minimal in-memory TF-IDF index over a document corpus."""

    def __init__(self):
        self.documents: List[Document] = []
        self._doc_term_freqs: List[Counter] = []
        self._doc_freq: Counter = Counter()
        self._idf: Dict[str, float] = {}
        self._doc_norms: List[float] = []
        self._built = False

    def load_corpus_dir(self, corpus_dir: str | Path) -> "TfidfVectorStore":
        corpus_dir = Path(corpus_dir)
        for path in sorted(corpus_dir.glob("*.txt")):
            raw_text = path.read_text(encoding="utf-8")

            symbol_match = re.search(r"^SYMBOL:\s*(\w+)", raw_text, re.MULTILINE)
            symbol = symbol_match.group(1).upper() if symbol_match else "UNKNOWN"

            for i, chunk_text in enumerate(_split_into_chunks(raw_text)):
                doc = Document(
                    doc_id=f"{path.stem}::chunk{i}",
                    source=path.name,
                    symbol=symbol,
                    chunk_id=i,
                    text=chunk_text,
                )
                self.documents.append(doc)
        self._build_index()
        return self

    def _build_index(self) -> None:
        self._doc_term_freqs = []
        self._doc_freq = Counter()

        for doc in self.documents:
            tf = Counter(tokenize(doc.text))
            self._doc_term_freqs.append(tf)
            for term in tf:
                self._doc_freq[term] += 1

        n_docs = max(1, len(self.documents))
        self._idf = {
            term: math.log((1 + n_docs) / (1 + df)) + 1.0
            for term, df in self._doc_freq.items()
        }

        self._doc_norms = []
        for tf in self._doc_term_freqs:
            norm = math.sqrt(sum((tf[t] * self._idf.get(t, 0.0)) ** 2 for t in tf))
            self._doc_norms.append(norm or 1e-9)

        self._built = True

    def query(self, query_text: str, top_k: int = 3, symbol_filter: str | None = None) -> List[RetrievedChunk]:
        if not self._built or not self.documents:
            return []

        q_tf = Counter(tokenize(query_text))
        q_vec = {t: q_tf[t] * self._idf.get(t, 0.0) for t in q_tf}
        q_norm = math.sqrt(sum(v ** 2 for v in q_vec.values())) or 1e-9

        scores = []
        for idx, doc in enumerate(self.documents):
            if symbol_filter and doc.symbol != symbol_filter.upper():
                continue

            tf = self._doc_term_freqs[idx]
            dot = 0.0
            for term, q_weight in q_vec.items():
                if term in tf:
                    dot += q_weight * (tf[term] * self._idf.get(term, 0.0))

            sim = dot / (q_norm * self._doc_norms[idx])
            if sim > 0:
                scores.append((sim, doc))

        scores.sort(key=lambda pair: pair[0], reverse=True)
        return [RetrievedChunk(document=d, score=round(s, 4)) for s, d in scores[:top_k]]
