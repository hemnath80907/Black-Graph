"""
Synthesis Agent
-----------------
Combines Technical, Fundamental, Sentiment and RAG agent outputs into one
explainable recommendation.

Two behaviours make this satisfy the problem statement's requirements:

1. Personalization: the vote is a WEIGHTED vote, not a flat majority. Weights
   come from the user's risk-tolerance profile (see personalization.risk_engine
   .get_agent_weights). Identical market inputs therefore produce different
   final signals/confidence for different user profiles.

2. Degraded-data resilience: any agent whose `degraded` flag is True is
   excluded from the vote and its weight is redistributed proportionally
   across the remaining agents, so a missing feed lowers confidence and is
   surfaced to the user, but never crashes the pipeline or silently produces
   an uncited claim.
"""

SIGNAL_VALUE = {"BUY": 1, "SELL": -1, "HOLD": 0}


def run(agent_results: list[dict], agent_weights: dict) -> dict:
    active = [r for r in agent_results if not r.get("degraded")]
    degraded = [r for r in agent_results if r.get("degraded")]

    if not active:
        return {
            "agent": "Synthesis Agent",
            "final_signal": "HOLD",
            "confidence": 0,
            "weighted_score": 0.0,
            "agent_summary": {r["agent"]: r["signal"] for r in agent_results},
            "degraded_agents": [r["agent"] for r in degraded],
            "citations": [],
            "reasons": ["All data feeds degraded; no signal can be responsibly issued."],
            "decision": "HOLD — insufficient live data across all agents.",
        }

    active_weight_total = sum(agent_weights.get(r["agent"], 0.0) for r in active)
    if active_weight_total <= 0:
        active_weight_total = 1.0
    normalized_weights = {
        r["agent"]: agent_weights.get(r["agent"], 0.0) / active_weight_total for r in active
    }

    weighted_score = sum(
        normalized_weights[r["agent"]] * SIGNAL_VALUE[r["signal"]] for r in active
    )
    weighted_confidence = sum(
        normalized_weights[r["agent"]] * r["confidence"] for r in active
    )

    if weighted_score >= 0.25:
        final_signal = "BUY"
    elif weighted_score <= -0.25:
        final_signal = "SELL"
    else:
        final_signal = "HOLD"

    # Confidence penalty proportional to how much weight was lost to degraded feeds.
    degraded_weight_lost = sum(agent_weights.get(r["agent"], 0.0) for r in degraded)
    confidence = round(weighted_confidence * (1 - 0.5 * degraded_weight_lost))
    confidence = max(0, min(99, confidence))

    citations = []
    for r in active:
        if r["agent"] == "RAG Agent":
            citations.extend(r.get("citations", []))

    buy_count = sum(1 for r in active if r["signal"] == "BUY")
    sell_count = sum(1 for r in active if r["signal"] == "SELL")
    hold_count = sum(1 for r in active if r["signal"] == "HOLD")

    decision_parts = [
        f"{buy_count} active agent(s) recommend BUY, {sell_count} recommend SELL, "
        f"{hold_count} recommend HOLD (weighted score {weighted_score:+.2f})."
    ]
    if degraded:
        names = ", ".join(r["agent"] for r in degraded)
        decision_parts.append(
            f"{len(degraded)} agent(s) degraded and excluded from the vote: {names}. "
            f"Remaining agent weights were renormalized; confidence reduced accordingly."
        )

    reasons = []
    for r in active:
        reasons.append(f"[{r['agent']}] {'; '.join(r['reasons'])}")
    for r in degraded:
        reasons.append(f"[{r['agent']} — DEGRADED] {'; '.join(r['reasons'])}")

    return {
        "agent": "Synthesis Agent",
        "final_signal": final_signal,
        "confidence": confidence,
        "weighted_score": round(weighted_score, 3),
        "weights_applied": normalized_weights,
        "agent_summary": {r["agent"]: r["signal"] for r in agent_results},
        "degraded_agents": [r["agent"] for r in degraded],
        "citations": citations,
        "reasons": reasons,
        "decision": " ".join(decision_parts),
    }
