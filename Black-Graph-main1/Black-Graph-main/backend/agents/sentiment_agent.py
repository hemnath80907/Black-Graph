"""
Sentiment Agent
----------------
Dimension: news flow polarity and aggregate market sentiment score.
"""

REQUIRED_FIELDS = ["positive_news", "negative_news", "sentiment_score"]


def run(stock_data: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if f not in stock_data or stock_data[f] is None]
    if missing:
        return {
            "agent": "Sentiment Agent",
            "dimension": "sentiment",
            "degraded": True,
            "signal": "HOLD",
            "confidence": 0,
            "reasons": [f"Data feed unavailable: missing field(s) {', '.join(missing)}."],
            "sentiment": {},
        }

    positive_news = stock_data["positive_news"]
    negative_news = stock_data["negative_news"]
    sentiment_score = stock_data["sentiment_score"]

    score = 0
    reasons = []

    if positive_news > negative_news:
        score += 1
        reasons.append(f"Positive news items ({positive_news}) outnumber negative ({negative_news}).")
    elif negative_news > positive_news:
        score -= 1
        reasons.append(f"Negative news items ({negative_news}) outnumber positive ({positive_news}).")
    else:
        reasons.append("Positive and negative news flow are balanced.")

    if sentiment_score >= 0.3:
        score += 1
        reasons.append(f"Aggregate sentiment score of {sentiment_score} is positive.")
    elif sentiment_score <= -0.3:
        score -= 1
        reasons.append(f"Aggregate sentiment score of {sentiment_score} is negative.")
    else:
        reasons.append(f"Aggregate sentiment score of {sentiment_score} is neutral.")

    if score >= 2:
        signal = "BUY"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = {2: 85, 1: 65}.get(abs(score), 50)

    return {
        "agent": "Sentiment Agent",
        "dimension": "sentiment",
        "degraded": False,
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "sentiment": {
            "positive_news": positive_news,
            "negative_news": negative_news,
            "sentiment_score": sentiment_score,
        },
    }
