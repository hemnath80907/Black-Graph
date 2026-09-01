# Black-Graph — Architecture & Decision Logic

Multi-agent autonomous financial intelligence system built for **PS-01** at
HACKVERSE: Into the Web, Sprint 1 (VIT Chennai, 2026).

## 1. What it does

Given a stock symbol and an investor profile, Black-Graph runs four
independent analysis agents in parallel, grounds one of them in real
regulatory filings and earnings-call transcripts with visible source
attribution, personalizes the outcome to the specific investor's risk
profile, synthesizes a single explainable recommendation, and logs
performance metrics for every session — all rendered live in a dashboard
that shows the full reasoning chain.

## 2. Pipeline overview

```
 simulated live feed        document corpus (SEBI filings,
 (data/market_data.json)     earnings transcripts)
        |                              |
        v                              v
 +-------------------------------------------------+
 |            PARALLEL AGENT DISPATCH               |
 |  (LangGraph, falls back to ThreadPoolExecutor)    |
 |                                                    |
 |  Technical Agent   Fundamental Agent               |
 |  Sentiment Agent   RAG Agent (TF-IDF retrieval)     |
 +-------------------------------------------------+
                    |
                    v
        each agent result carries:
        { signal, confidence, reasons[], degraded: bool }
                    |
                    v
 +-------------------------------------------------+
 |   PERSONALIZATION (personalization/risk_engine)  |
 |   risk_tolerance -> per-agent vote weights        |
 +-------------------------------------------------+
                    |
                    v
 +-------------------------------------------------+
 |         SYNTHESIS AGENT (weighted vote)           |
 |  excludes/reweights degraded agents, never         |
 |  fabricates a claim it cannot cite                 |
 +-------------------------------------------------+
                    |
                    v
 +-------------------------------------------------+
 |   PERFORMANCE LOG (SQLite): latency, accuracy      |
 |   proxy vs 30-day forward return, portfolio risk   |
 |   concentration, degraded-agent count              |
 +-------------------------------------------------+
                    |
                    v
              live dashboard (frontend/index.html)
```

## 3. Agents and their reasoning

| Agent | Dimension | Signal logic |
|---|---|---|
| **Technical** | price momentum | Scores price vs. 20-day SMA, RSI, and volume vs. average; each factor contributes +1/0/-1 to a signed score that maps to BUY/HOLD/SELL. |
| **Fundamental** | company financials | Scores revenue growth, profit growth, and debt ratio the same way. |
| **Sentiment** | news/market mood | Scores positive-vs-negative news counts and an aggregate sentiment score. |
| **RAG** | regulatory/disclosure grounding | Retrieves the most relevant chunks from SEBI filings and earnings-call transcripts for the symbol (TF-IDF cosine similarity, implemented from scratch in `retrieval/vector_store.py`), scores the retrieved text's qualitative tone (risk terms vs. growth terms), and returns the signal **with the source document, snippet, and relevance score attached**. If nothing meets the relevance threshold, it reports itself as degraded instead of guessing. |

Each agent independently returns a structured contract:
`{agent, signal, confidence, reasons[], degraded}` (plus agent-specific
fields like `citations` for RAG), which the synthesis layer consumes.

## 4. Personalization: same market data, different investors, different output

`personalization/risk_engine.get_agent_weights(risk_tolerance)` maps a
user's risk tolerance to a set of per-agent vote weights:

- **LOW** risk tolerance leans on Fundamental + RAG (regulatory grounding),
  discounts short-term Technical/Sentiment noise.
- **HIGH** risk tolerance leans on Technical + Sentiment momentum, discounts
  slow-moving Fundamentals.
- **MODERATE** is balanced.

The Synthesis Agent then computes a **weighted** vote (not a flat majority),
so identical market inputs can and do produce different final signals for
different investors — verified in `backend/tests/test_pipeline.py`, e.g.
TCS resolves to `HOLD` for a low-risk-tolerance investor and `SELL` for a
high-risk-tolerance investor on the same data.

Separately, `risk_engine.analyze_user()` combines portfolio concentration,
recent trading behavior, and the stated risk tolerance into an overall risk
score, which drives plain-language guidance and warnings shown alongside
the synthesized signal.

## 5. Degraded-data handling

Every agent validates its own required inputs and returns
`degraded: True` with a labeled reason instead of raising when a field is
missing. The orchestrator additionally wraps every node in a try/except so
an unexpected exception is isolated to that agent rather than crashing the
run. The Synthesis Agent excludes degraded agents from the vote,
redistributes their weight across the remaining agents, and reduces overall
confidence proportionally to the weight lost — and it never emits an
RAG-sourced claim without a citation.

Four scenarios are wired into the demo via `degraded/fault_injection.py`
and selectable from the dashboard: a missing technical feed, a missing
sentiment feed, a missing regulatory filing, and a conflicting-signals case
where sentiment and fundamentals disagree sharply.

## 6. Performance log

Every analysis session is written to SQLite (`logging_/performance_log.py`)
with: per-agent and total latency, a signal-accuracy proxy (does the
signal's direction match the recorded 30-day forward return?), the
investor's portfolio risk concentration, and the count of degraded agents
in that run. The dashboard's "Performance log" panel reads this back live.

## 7. Known simplifications (hackathon scope)

- Market data and the document corpus are static, versioned JSON/text files
  rather than live NSE/SEBI feeds — the ingestion boundary
  (`data/market_data.json`, `data/corpus/*.txt`) is where a real feed would
  be substituted without touching agent logic.
- Retrieval is TF-IDF, not a learned embedding model, so it's dependency-free
  and fully offline-testable; the `TfidfVectorStore.query()` contract is
  designed to be swapped for an embeddings-based store later.
- The accuracy-proxy metric compares against a pre-recorded forward return
  rather than a live market close, since the demo has no live market feed.
