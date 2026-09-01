def technical_agent(stock_data):
    """
    Prototype Technical Analysis Agent
    """

    price = stock_data["price"]
    sma20 = stock_data["sma20"]
    rsi = stock_data["rsi"]
    volume = stock_data["volume"]
    avg_volume = stock_data["avg_volume"]

    score = 0
    reasons = []

    # 1. Price momentum
    if price > sma20:
        score += 1
        reasons.append("Price is above the 20-day moving average")
    else:
        score -= 1
        reasons.append("Price is below the 20-day moving average")

    # 2. RSI
    if rsi > 55:
        score += 1
        reasons.append("RSI shows positive momentum")
    elif rsi < 45:
        score -= 1
        reasons.append("RSI shows weak momentum")
    else:
        reasons.append("RSI is neutral")

    # 3. Volume
    if volume > avg_volume:
        score += 1
        reasons.append("Trading volume is above average")
    else:
        reasons.append("Trading volume is below average")

    # Final signal
    if score >= 2:
        signal = "BUY"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    # Confidence
    if abs(score) == 3:
        confidence = 90
    elif abs(score) == 2:
        confidence = 75
    else:
        confidence = 60

    # Return structured result
    return {
        "agent": "Technical Agent",
        "signal": signal,
        "confidence": confidence,
        "indicators": {
            "price": price,
            "sma20": sma20,
            "rsi": rsi,
            "volume": volume,
            "average_volume": avg_volume
        },
        "reasons": reasons
    }


# -----------------------------
# PROTOTYPE TEST DATA
# -----------------------------

stock_data = {
    "price": 1520,
    "sma20": 1480,
    "rsi": 63,
    "volume": 1500000,
    "avg_volume": 1000000
}


# Run Technical Agent
result = technical_agent(stock_data)


# Display result
print("\n===== TECHNICAL AGENT =====")
print("Signal:", result["signal"])
print("Confidence:", result["confidence"], "%")

print("\nIndicators:")
for key, value in result["indicators"].items():
    print(key, ":", value)

print("\nReasons:")
for reason in result["reasons"]:
    print("-", reason)