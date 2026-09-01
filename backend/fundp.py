def fundamental_agent(stock_data):
    """
    Prototype Fundamental Analysis Agent
    """

    revenue_growth = stock_data["revenue_growth"]
    profit_growth = stock_data["profit_growth"]
    debt_ratio = stock_data["debt_ratio"]

    score = 0
    reasons = []

    # 1. Revenue Growth
    if revenue_growth > 10:
        score += 1
        reasons.append("Revenue growth is strong")

    elif revenue_growth < 0:
        score -= 1
        reasons.append("Revenue is declining")

    else:
        reasons.append("Revenue growth is moderate")

    # 2. Profit Growth
    if profit_growth > 10:
        score += 1
        reasons.append("Profit growth is strong")

    elif profit_growth < 0:
        score -= 1
        reasons.append("Profit is declining")

    else:
        reasons.append("Profit growth is moderate")

    # 3. Debt
    if debt_ratio < 0.5:
        score += 1
        reasons.append("Debt level is relatively low")

    elif debt_ratio > 1:
        score -= 1
        reasons.append("Debt level is relatively high")

    else:
        reasons.append("Debt level is moderate")

    # -----------------------------
    # Final Signal
    # -----------------------------

    if score >= 2:
        signal = "BUY"

    elif score <= -1:
        signal = "SELL"

    else:
        signal = "HOLD"

    # -----------------------------
    # Confidence
    # -----------------------------

    if abs(score) == 3:
        confidence = 90

    elif abs(score) == 2:
        confidence = 75

    else:
        confidence = 60

    # -----------------------------
    # Return Result
    # -----------------------------

    return {
        "agent": "Fundamental Agent",
        "signal": signal,
        "confidence": confidence,

        "metrics": {
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth,
            "debt_ratio": debt_ratio
        },

        "reasons": reasons
    }


# ==================================
# PROTOTYPE TEST DATA
# ==================================

stock_data = {
    "revenue_growth": 15,
    "profit_growth": 18,
    "debt_ratio": 0.35
}


# Run Fundamental Agent
result = fundamental_agent(stock_data)


# Display result
print("\n===== FUNDAMENTAL AGENT =====")

print("Signal:", result["signal"])

print("Confidence:", result["confidence"], "%")


print("\nFinancial Metrics:")

for key, value in result["metrics"].items():
    print(key, ":", value)


print("\nReasons:")

for reason in result["reasons"]:
    print("-", reason)