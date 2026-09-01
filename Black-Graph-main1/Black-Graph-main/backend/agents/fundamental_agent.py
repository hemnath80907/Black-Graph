"""
Fundamental Analysis Agent
---------------------------
Dimension: revenue growth, profit growth, and balance-sheet leverage.
"""

REQUIRED_FIELDS = ["revenue_growth", "profit_growth", "debt_ratio"]


def run(stock_data: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if f not in stock_data or stock_data[f] is None]
    if missing:
        return {
            "agent": "Fundamental Agent",
            "dimension": "fundamentals",
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [f"Data feed unavailable: missing field(s) {', '.join(missing)}."],
            "metrics": {},
        }

    revenue_growth = stock_data["revenue_growth"]
    profit_growth = stock_data["profit_growth"]
    debt_ratio = stock_data["debt_ratio"]

    score = 0
    reasons = []

    if revenue_growth > 10:
        score += 1
        reasons.append(f"Revenue growth of {revenue_growth}% is strong.")
    elif revenue_growth < 0:
        score -= 1
        reasons.append(f"Revenue is declining ({revenue_growth}%).")
    else:
        reasons.append(f"Revenue growth of {revenue_growth}% is moderate.")

    if profit_growth > 10:
        score += 1
        reasons.append(f"Profit growth of {profit_growth}% is strong.")
    elif profit_growth < 0:
        score -= 1
        reasons.append(f"Profit is declining ({profit_growth}%).")
    else:
        reasons.append(f"Profit growth of {profit_growth}% is moderate.")

    if debt_ratio < 0.5:
        score += 1
        reasons.append(f"Debt ratio of {debt_ratio} is relatively low.")
    elif debt_ratio > 1:
        score -= 1
        reasons.append(f"Debt ratio of {debt_ratio} is relatively high.")
    else:
        reasons.append(f"Debt ratio of {debt_ratio} is moderate.")

    if score >= 2:
        signal = "BUY"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = {3: 90, 2: 75}.get(abs(score), 60)

    return {
        "agent": "Fundamental Agent",
        "dimension": "fundamentals",
        "degraded": False,
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "metrics": {
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "debt_ratio": debt_ratio,
        },
    }
