"""
Multi-Agent Orchestrator
--------------------------
Dispatches the Technical, Fundamental, Sentiment and RAG agents IN PARALLEL
using LangGraph, then fans their outputs into the Synthesis agent.

Each node is wrapped so that an unexpected exception (not just a missing
field, which the agents already handle themselves) is caught and turned into
a labeled "degraded" result instead of crashing the whole pipeline run. This
is what satisfies "graceful handling of a degraded-data scenario ... without
the pipeline failing".

If LangGraph is not installed, `run_pipeline` transparently falls back to a
ThreadPoolExecutor-based parallel dispatch that has the identical contract,
so the API layer never needs to know which execution path was used.
"""

from __future__ import annotations

import time
from typing import TypedDict

from agents import technical_agent, fundamental_agent, sentiment_agent, rag_agent, synthesis_agent
from retrieval.vector_store import TfidfVectorStore

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class AgentState(TypedDict, total=False):
    symbol: str
    stock_data: dict
    force_rag_degraded: bool
    retriever: TfidfVectorStore
    agent_weights: dict

    technical_result: dict
    fundamental_result: dict
    sentiment_result: dict
    rag_result: dict
    synthesis_result: dict

    latency_ms: dict


def _safe_run(agent_name: str, fn, *args) -> tuple[dict, float]:
    start = time.perf_counter()
    try:
        result = fn(*args)
    except Exception as exc:  # noqa: BLE001 - deliberate: never crash the pipeline
        result = {
            "agent": agent_name,
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [f"Agent raised an unexpected error and was isolated: {exc!r}"],
        }
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return result, elapsed_ms


# --------------------------------------------------------------------------
# LangGraph node functions
# --------------------------------------------------------------------------

def _technical_node(state: AgentState) -> dict:
    result, ms = _safe_run("Technical Agent", technical_agent.run, state["stock_data"])
    return {"technical_result": result, "latency_ms": {"technical": ms}}


def _fundamental_node(state: AgentState) -> dict:
    result, ms = _safe_run("Fundamental Agent", fundamental_agent.run, state["stock_data"])
    return {"fundamental_result": result, "latency_ms": {"fundamental": ms}}


def _sentiment_node(state: AgentState) -> dict:
    result, ms = _safe_run("Sentiment Agent", sentiment_agent.run, state["stock_data"])
    return {"sentiment_result": result, "latency_ms": {"sentiment": ms}}


def _rag_node(state: AgentState) -> dict:
    if state.get("force_rag_degraded"):
        result = {
            "agent": "RAG Agent",
            "dimension": "regulatory_disclosure",
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": ["Simulated scenario: the regulatory filing feed for this symbol is unavailable."],
            "citations": [],
        }
        ms = 0.0
    else:
        result, ms = _safe_run(
            "RAG Agent", rag_agent.run, state["symbol"], state["stock_data"], state["retriever"]
        )
    return {"rag_result": result, "latency_ms": {"rag": ms}}


def _synthesis_node(state: AgentState) -> dict:
    agent_results = [
        state["technical_result"],
        state["fundamental_result"],
        state["sentiment_result"],
        state["rag_result"],
    ]
    result, ms = _safe_run(
        "Synthesis Agent", synthesis_agent.run, agent_results, state["agent_weights"]
    )
    return {"synthesis_result": result, "latency_ms": {"synthesis": ms}}


def _reduce_latency(*latency_dicts: dict) -> dict:
    merged = {}
    for d in latency_dicts:
        merged.update(d)
    return merged


def _build_langgraph_app():
    builder = StateGraph(AgentState)

    builder.add_node("technical", _technical_node)
    builder.add_node("fundamental", _fundamental_node)
    builder.add_node("sentiment", _sentiment_node)
    builder.add_node("rag", _rag_node)
    builder.add_node("synthesis", _synthesis_node)

    for parallel_node in ("technical", "fundamental", "sentiment", "rag"):
        builder.add_edge(START, parallel_node)
        builder.add_edge(parallel_node, "synthesis")

    builder.add_edge("synthesis", END)

    return builder.compile()


_LANGGRAPH_APP = _build_langgraph_app() if LANGGRAPH_AVAILABLE else None


def _run_via_langgraph(symbol, stock_data, retriever, agent_weights, force_rag_degraded) -> dict:
    result = _LANGGRAPH_APP.invoke({
        "symbol": symbol,
        "stock_data": stock_data,
        "retriever": retriever,
        "agent_weights": agent_weights,
        "force_rag_degraded": force_rag_degraded,
    })
    return result


def _run_via_threadpool(symbol, stock_data, retriever, agent_weights, force_rag_degraded) -> dict:
    from concurrent.futures import ThreadPoolExecutor

    state: AgentState = {
        "symbol": symbol,
        "stock_data": stock_data,
        "retriever": retriever,
        "agent_weights": agent_weights,
        "force_rag_degraded": force_rag_degraded,
        "latency_ms": {},
    }

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            "technical": pool.submit(_technical_node, state),
            "fundamental": pool.submit(_fundamental_node, state),
            "sentiment": pool.submit(_sentiment_node, state),
            "rag": pool.submit(_rag_node, state),
        }
        for name, future in futures.items():
            partial = future.result()
            state.update(partial)
            state["latency_ms"].update(partial["latency_ms"])

    synth_partial = _synthesis_node(state)
    state.update(synth_partial)
    state["latency_ms"].update(synth_partial["latency_ms"])
    return state


def run_pipeline(
    symbol: str,
    stock_data: dict,
    retriever: TfidfVectorStore,
    agent_weights: dict,
    scenario: str = "none",
) -> dict:
    """Runs the full parallel multi-agent pipeline for one symbol and returns
    the merged final state (all agent results + synthesis + latency log)."""

    from degraded.fault_injection import apply as apply_fault

    mutated_stock_data, force_rag_degraded = apply_fault(stock_data, scenario)

    runner = _run_via_langgraph if LANGGRAPH_AVAILABLE else _run_via_threadpool
    return runner(symbol, mutated_stock_data, retriever, agent_weights, force_rag_degraded)
