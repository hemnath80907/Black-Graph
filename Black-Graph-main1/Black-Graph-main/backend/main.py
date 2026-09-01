"""
Black-Graph — Multi-Agent Autonomous Financial Intelligence System
=====================================================================
FastAPI entrypoint. Wires together:

  data ingestion (data/market_data.json, simulated live feed)
     -> parallel multi-agent reasoning (orchestrator.run_pipeline)
        - Technical Agent
        - Fundamental Agent
        - Sentiment Agent
        - RAG Agent (grounded in data/corpus/*.txt, cited)
     -> personalization (personalization/risk_engine.py: per-user agent
        weighting + risk scoring)
     -> synthesis (agents/synthesis_agent.py: weighted vote, degraded-agent
        aware)
     -> performance logging (logging_/performance_log.py, SQLite)

Run with:  uvicorn main:api --reload --port 8000
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from retrieval.vector_store import TfidfVectorStore
from personalization.risk_engine import (
    get_agent_weights,
    analyze_user,
)
from personalization.models import UserProfile, Portfolio, BehaviorData
from orchestrator import run_pipeline, LANGGRAPH_AVAILABLE
from logging_.performance_log import log_session, get_recent_sessions, get_aggregate_metrics
from degraded.fault_injection import VALID_SCENARIOS

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Load static demo data (simulated live feeds) once at startup.
# ---------------------------------------------------------------------------

MARKET_DATA: dict = json.loads((DATA_DIR / "market_data.json").read_text())
USERS: dict = json.loads((DATA_DIR / "users.json").read_text())

RETRIEVER = TfidfVectorStore().load_corpus_dir(DATA_DIR / "corpus")


api = FastAPI(
    title="Black-Graph — Multi-Agent Financial Intelligence API",
    description="Explainable, personalized, RAG-grounded investment intelligence for retail investors.",
    version="2.0",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    symbol: str
    user_id: str
    scenario: Optional[str] = "none"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api.get("/")
def home():
    return {
        "message": "Black-Graph Multi-Agent Financial Intelligence API is running",
        "orchestration_engine": "langgraph" if LANGGRAPH_AVAILABLE else "threadpool-fallback",
        "symbols_available": list(MARKET_DATA.keys()),
        "corpus_chunks_indexed": len(RETRIEVER.documents),
    }


@api.get("/api/symbols")
def list_symbols():
    return [
        {"symbol": sym, "name": data["name"]}
        for sym, data in MARKET_DATA.items()
    ]


@api.get("/api/users")
def list_users():
    return list(USERS.values())


@api.get("/api/scenarios")
def list_scenarios():
    return sorted(VALID_SCENARIOS)


@api.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    symbol = req.symbol.upper()
    if symbol not in MARKET_DATA:
        raise HTTPException(status_code=404, detail=f"Unknown symbol '{symbol}'.")

    if req.user_id not in USERS:
        raise HTTPException(status_code=404, detail=f"Unknown user '{req.user_id}'.")

    if req.scenario not in VALID_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{req.scenario}'.")

    stock_row = MARKET_DATA[symbol]
    flat_market_data = {
        **stock_row["technical"],
        **stock_row["fundamental"],
        **stock_row["sentiment"],
    }

    user_row = USERS[req.user_id]
    user = UserProfile(
        user_id=user_row["user_id"],
        risk_tolerance=user_row["risk_tolerance"],
        investment_goal=user_row["investment_goal"],
        investment_horizon=user_row["investment_horizon"],
    )
    portfolio = Portfolio(holdings=user_row["portfolio"])
    behavior = BehaviorData(**user_row["behavior"])

    agent_weights = get_agent_weights(user.risk_tolerance)

    # ---- 1. Parallel multi-agent reasoning (with degraded-scenario injection) ----
    pipeline_result = run_pipeline(
        symbol=symbol,
        stock_data=flat_market_data,
        retriever=RETRIEVER,
        agent_weights=agent_weights,
        scenario=req.scenario,
    )
    synthesis = pipeline_result["synthesis_result"]

    # ---- 2. Personalization / risk scoring, using the synthesized signal ----
    risk_profile = analyze_user(user, portfolio, behavior, synthesis["final_signal"])

    # ---- 3. Performance logging ----
    log_row = log_session(
        symbol=symbol,
        user_id=user.user_id,
        scenario=req.scenario,
        synthesis_result=synthesis,
        latency_ms=pipeline_result["latency_ms"],
        forward_return_pct=stock_row.get("forward_return_30d_pct"),
        portfolio_risk_concentration=risk_profile["portfolio_concentration"],
    )

    # ---- 4. Assemble full, explainable response for the live interface ----
    return {
        "symbol": symbol,
        "stock_name": stock_row["name"],
        "scenario_simulated": req.scenario,
        "orchestration_engine": "langgraph" if LANGGRAPH_AVAILABLE else "threadpool-fallback",
        "agents": {
            "technical": pipeline_result["technical_result"],
            "fundamental": pipeline_result["fundamental_result"],
            "sentiment": pipeline_result["sentiment_result"],
            "rag": pipeline_result["rag_result"],
        },
        "synthesis": synthesis,
        "personalization": risk_profile,
        "performance_log_entry": log_row,
        "reasoning_chain": [
            "1. Data ingestion: live/simulated market feed + document corpus loaded.",
            "2. Parallel dispatch: Technical, Fundamental, Sentiment, RAG agents run concurrently.",
            "3. RAG retrieval: top passages retrieved from filings/transcripts via TF-IDF, attribution attached.",
            "4. Personalization: agent vote weights selected from the user's risk-tolerance profile.",
            "5. Synthesis: weighted vote combines active agents; degraded agents excluded and flagged.",
            "6. Risk scoring: portfolio concentration + behavior + profile risk combined into guidance.",
            "7. Logging: latency, accuracy proxy, and risk concentration persisted for this session.",
        ],
    }


@api.get("/api/logs")
def logs(limit: int = 25):
    return {
        "recent_sessions": get_recent_sessions(limit=limit),
        "aggregate_metrics": get_aggregate_metrics(),
    }
