"""
Fault injection for the "graceful handling of a degraded-data scenario"
requirement. Lets the demo operator (via the UI toggle or API flag) simulate:

  - an unavailable technical/fundamental/sentiment feed (fields stripped out)
  - a missing regulatory filing (RAG retrieval forced empty)
  - a conflicting-signal scenario (sentiment flipped hard negative while
    fundamentals stay strongly positive) to show the synthesis layer
    reasoning through disagreement rather than failing.

Nothing here ever raises — it only mutates the input in predictable, labeled
ways so the rest of the pipeline exercises its real degraded-data handling
paths instead of a separately-tested mock.
"""

from copy import deepcopy

VALID_SCENARIOS = {
    "none",
    "technical_feed_down",
    "fundamental_feed_down",
    "sentiment_feed_down",
    "filing_unavailable",
    "conflicting_signals",
}


def apply(stock_data: dict, scenario: str) -> tuple[dict, bool]:
    """
    Returns (possibly-mutated stock_data copy, force_rag_degraded: bool).
    """
    scenario = scenario if scenario in VALID_SCENARIOS else "none"
    data = deepcopy(stock_data)
    force_rag_degraded = False

    if scenario == "technical_feed_down":
        for f in ("price", "sma20", "rsi", "volume", "avg_volume"):
            data.pop(f, None)

    elif scenario == "fundamental_feed_down":
        for f in ("revenue_growth", "profit_growth", "debt_ratio"):
            data.pop(f, None)

    elif scenario == "sentiment_feed_down":
        for f in ("positive_news", "negative_news", "sentiment_score"):
            data.pop(f, None)

    elif scenario == "filing_unavailable":
        force_rag_degraded = True

    elif scenario == "conflicting_signals":
        data["sentiment_score"] = -0.95
        data["negative_news"] = data.get("negative_news", 0) + 10
        data["positive_news"] = 0

    return data, force_rag_degraded
