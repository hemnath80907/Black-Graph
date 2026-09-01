def synthesis_agent(technical, fundamental, sentiment):
    """
    Prototype Synthesis Agent
    Combines Technical, Fundamental and Sentiment results.
    """

    results = [
        technical,
        fundamental,
        sentiment
    ]

    buy_count = 0
    sell_count = 0
    hold_count = 0

    total_confidence = 0
    reasons = []

    # --------------------------------
    # Collect agent results
    # --------------------------------

    for result in results:

        signal = result["signal"]
        confidence = result["confidence"]

        total_confidence += confidence

        if signal == "BUY":
            buy_count += 1

        elif signal == "SELL":
            sell_count += 1

        else:
            hold_count += 1

        reasons.extend(result["reasons"])

    # --------------------------------
    # Final decision
    # --------------------------------

    if buy_count >= 2:
        final_signal = "BUY"

    elif sell_count >= 2:
        final_signal = "SELL"

    else:
        final_signal = "HOLD"

    # --------------------------------
    # Average confidence
    # --------------------------------

    confidence = round(total_confidence / len(results))

    # --------------------------------
    # Return final result
    # --------------------------------

    return {
        "agent": "Synthesis Agent",

        "final_signal": final_signal,

        "confidence": confidence,

        "agent_summary": {
            "technical": technical["signal"],
            "fundamental": fundamental["signal"],
            "sentiment": sentiment["signal"]
        },

        "reasons": reasons,

        "decision": (
            f"{buy_count} agents recommend BUY, "
            f"{sell_count} recommend SELL, "
            f"{hold_count} recommend HOLD."
        )
    }