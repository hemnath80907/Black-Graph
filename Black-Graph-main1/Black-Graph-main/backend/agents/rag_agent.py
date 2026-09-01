"""
RAG Agent (Regulatory / Disclosure Grounding)
-----------------------------------------------
Dimension: qualitative signal extracted from regulatory filings and earnings
call transcripts, retrieved via the TF-IDF vector store and always returned
with source attribution (document name + retrieval score + snippet).

This agent is the "at least one agent output grounded in retrieved source
material, with attribution visible to the user" requirement. If retrieval
finds nothing relevant above the similarity threshold, the agent degrades
gracefully rather than emitting an uncited claim.
"""

from retrieval.vector_store import TfidfVectorStore

MIN_RELEVANCE_SCORE = 0.05

RISK_TERMS = [
    "risk", "litigation", "dispute", "decline", "declining", "pressure",
    "compress", "compressed", "volatility", "uncertain", "uncertainty",
    "moderating", "moderate", "deceleration", "softness", "muted",
    "elongated", "attrition", "adverse",
]

POSITIVE_TERMS = [
    "growth", "improved", "improvement", "strong", "confidence", "momentum",
    "expansion", "reiterate", "reiterated", "upsell", "recovery", "renewed",
    "debt-free", "deleveraging", "stabilize", "stabilized",
]


def _score_text(text: str) -> int:
    lowered = text.lower()
    score = 0
    score += sum(lowered.count(term) for term in POSITIVE_TERMS)
    score -= sum(lowered.count(term) for term in RISK_TERMS)
    return score


def run(symbol: str, stock_data: dict, retriever: TfidfVectorStore) -> dict:
    query = (
        f"{symbol} revenue growth debt risk factors litigation guidance "
        f"margin outlook contingent liabilities"
    )
    hits = retriever.query(query, top_k=4, symbol_filter=symbol)
    hits = [h for h in hits if h.score >= MIN_RELEVANCE_SCORE]

    if not hits:
        return {
            "agent": "RAG Agent",
            "dimension": "regulatory_disclosure",
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [
                f"No filing or transcript in the corpus meets the relevance "
                f"threshold for {symbol}; degrading rather than producing an "
                f"uncited claim."
            ],
            "citations": [],
        }

    net_score = sum(_score_text(h.document.text) for h in hits)

    if net_score >= 2:
        signal = "BUY"
    elif net_score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    avg_relevance = sum(h.score for h in hits) / len(hits)
    confidence = min(90, round(55 + avg_relevance * 100))

    citations = [
        {
            "source": h.document.source,
            "relevance_score": h.score,
            "snippet": (h.document.text[:220] + "...") if len(h.document.text) > 220 else h.document.text,
        }
        for h in hits
    ]

    reasons = [
        f"Retrieved {len(hits)} relevant passage(s) from {len({h.document.source for h in hits})} "
        f"source document(s); net qualitative tone score {net_score:+d}.",
        f"Top source: {citations[0]['source']} (relevance {citations[0]['relevance_score']}).",
    ]

    return {
        "agent": "RAG Agent",
        "dimension": "regulatory_disclosure",
        "degraded": False,
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "citations": citations,
    }
