def sentiment_agent(stock_data):
    """
    Prototype Sentiment Analysis Agent
    """

    positive_news = stock_data["positive_news"]
    negative_news = stock_data["negative_news"]
    sentiment_score = stock_data["sentiment_score"]

    score = 0
    reasons = []

    # -----------------------------
    # 1. Positive News
    # -----------------------------

    if positive_news > negative_news:
        score += 1
        reasons.append(
            "Positive news is higher than negative news"
        )

    elif negative_news > positive_news:
        score -= 1
        reasons.append(
            "Negative news is higher than positive news"
        )

    else:
        reasons.append(
            "Positive and negative news are balanced"
        )

    # -----------------------------
    # 2. Sentiment Score
    # -----------------------------

    if sentiment_score >= 0.5:
        score += 1
        reasons.append(
            "Overall market sentiment is positive"
        )

    elif sentiment_score <= -0.5:
        score -= 1
        reasons.append(
            "Overall market sentiment is negative"
        )

    else:
        reasons.append(
            "Overall market sentiment is neutral"
        )

    # -----------------------------
    # 3. Final Signal
    # -----------------------------

    if score >= 2:
        signal = "BUY"

    elif score <= -1:
        signal = "SELL"

    else:
        signal = "HOLD"

    # -----------------------------
    # 4. Confidence
    # -----------------------------

    if abs(score) == 2:
        confidence = 85

    elif abs(score) == 1:
        confidence = 65

    else:
        confidence = 50

    # -----------------------------
    # 5. Return Result
    # -----------------------------

    return {
        "agent": "Sentiment Agent",

        "signal": signal,

        "confidence": confidence,

        "sentiment": {
            "positive_news": positive_news,
            "negative_news": negative_news,
            "sentiment_score": sentiment_score
        },

        "reasons": reasons
    }


# ==================================
# PROTOTYPE TEST DATA
# ==================================

stock_data = {

    "positive_news": 8,

    "negative_news": 3,

    "sentiment_score": 0.7
}


# Run Sentiment Agent
result = sentiment_agent(stock_data)


# ==================================
# DISPLAY RESULT
# ==================================

print("\n===== SENTIMENT AGENT =====")

print("Signal:", result["signal"])

print("Confidence:", result["confidence"], "%")


print("\nSentiment Data:")

for key, value in result["sentiment"].items():
    print(key, ":", value)


print("\nReasons:")

for reason in result["reasons"]:
    print("-", reason)