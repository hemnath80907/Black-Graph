"""
Technical Analysis Agent
-------------------------
Dimension: price momentum, RSI, and volume behaviour.
Produces a classified signal with a stated confidence level and cited
reasoning (each reason ties back to a specific observed indicator value,
which is the "citation" for this agent's non-document dimension).
"""

REQUIRED_FIELDS = ["price", "sma20", "rsi", "volume", "avg_volume"]


def run(stock_data: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if f not in stock_data or stock_data[f] is None]
    if missing:
        return {
            "agent": "Technical Agent",
            "dimension": "price_momentum",
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [f"Data feed unavailable: missing field(s) {', '.join(missing)}."],
            "indicators": {},
        }

    price = stock_data["price"]
    sma20 = stock_data["sma20"]
    rsi = stock_data["rsi"]
    volume = stock_data["volume"]
    avg_volume = stock_data["avg_volume"]

    score = 0
    reasons = []

    if price > sma20:
        score += 1
        reasons.append(f"Price ({price}) is above the 20-day moving average ({sma20}).")
    else:
        score -= 1
        reasons.append(f"Price ({price}) is below the 20-day moving average ({sma20}).")

    if rsi > 55:
        score += 1
        reasons.append(f"RSI at {rsi} shows positive momentum.")
    elif rsi < 45:
        score -= 1
        reasons.append(f"RSI at {rsi} shows weak momentum.")
    else:
        reasons.append(f"RSI at {rsi} is neutral.")

    if volume > avg_volume:
        score += 1
        reasons.append(f"Trading volume ({volume:,}) is above the average ({avg_volume:,}).")
    else:
        reasons.append(f"Trading volume ({volume:,}) is below the average ({avg_volume:,}).")

    if score >= 2:
        signal = "BUY"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = {3: 90, 2: 75}.get(abs(score), 60)

    return {
        "agent": "Technical Agent",
        "dimension": "price_momentum",
        "degraded": False,
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "indicators": {
            "price": price,
            "sma20": sma20,
            "rsi": rsi,
            "volume": volume,
            "average_volume": avg_volume,
        },
    }
