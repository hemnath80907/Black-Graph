# Black-Graph

Multi-agent autonomous financial intelligence system for retail investors —
built for **PS-01: Multi-Agent Autonomous Financial Intelligence System for
Retail Investors**, HACKVERSE: Into the Web, Sprint 1 (IEEE RAS · VIT
Chennai, 2026).

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full agent architecture
and decision-logic writeup.

## What's inside

```
Black-Graph-main/
├── backend/
│   ├── main.py                  FastAPI app — the API judges/demo hit
│   ├── orchestrator.py          Parallel multi-agent dispatch (LangGraph, with a
│   │                            dependency-free ThreadPoolExecutor fallback)
│   ├── agents/
│   │   ├── technical_agent.py
│   │   ├── fundamental_agent.py
│   │   ├── sentiment_agent.py
│   │   ├── rag_agent.py         Retrieval-augmented, cites its sources
│   │   └── synthesis_agent.py   Weighted vote, degraded-agent aware
│   ├── retrieval/
│   │   └── vector_store.py      TF-IDF retriever, stdlib only
│   ├── personalization/
│   │   ├── risk_engine.py       Portfolio/behavior/profile risk + agent weighting
│   │   ├── behavior.py
│   │   ├── personalization.py
│   │   └── models.py
│   ├── logging_/
│   │   └── performance_log.py   SQLite session/performance log
│   ├── degraded/
│   │   └── fault_injection.py   Simulated degraded-data scenarios
│   ├── data/
│   │   ├── market_data.json     Simulated live market feed (3 stocks)
│   │   ├── users.json           3 demo investor profiles
│   │   └── corpus/*.txt         Synthetic SEBI filings & earnings transcripts
│   ├── tests/
│   │   └── test_pipeline.py     Sanity checks, no FastAPI/LangGraph required
│   └── requirements.txt
└── frontend/
    └── index.html               Live dashboard (open directly, no build step)
```

The original prototype code (two disconnected FastAPI apps, hardcoded
single-stock data, no RAG, no frontend, no logging) has been consolidated
and extended into the structure above. Nothing in `backend/` depends on the
old `backend/` or `backend1/` folders from the initial prototype.

## Running it

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
uvicorn main:api --reload --port 8000
```

The API is now live at `http://localhost:8000`. `GET /` reports which
orchestration engine is active (`langgraph` or the threadpool fallback, in
case LangGraph isn't installed).

Run the sanity checks any time (no server needed):

```bash
python3 tests/test_pipeline.py
```

### 2. Frontend

Open `frontend/index.html` directly in a browser (or serve it with any
static file server). It talks to `http://localhost:8000` by default — the
API base URL is editable at the top of the sidebar if you're running the
backend elsewhere.

### 3. Try the demo flow

1. Pick a symbol (`RELIANCE`, `TCS`, `INFY`) and an investor profile.
2. Run the analysis. Watch the four agents resolve in parallel, the RAG
   agent's cited sources, the synthesized signal, and the personalized
   guidance.
3. Switch the investor profile with the same symbol — TCS and INFY are
   deliberately set up so low- vs. high-risk-tolerance investors get a
   different final signal from identical market data.
4. Pick a degraded-data scenario from the sidebar and re-run — watch the
   affected agent mark itself degraded, get excluded from the vote, and the
   confidence drop accordingly, without the pipeline failing.
5. Check the performance log panel at the bottom for latency, the
   accuracy-vs-forward-return proxy, and risk-concentration metrics logged
   across your session runs.
