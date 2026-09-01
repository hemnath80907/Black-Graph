def generate_personalized_guidance(
    risk_tolerance,
    overall_risk_level,
    portfolio_risk,
    behavior_risk,
    market_signal,
):
    guidance = []
    warnings = []

    if risk_tolerance.upper() == "LOW":
        guidance.append(
            "The user has a low risk tolerance, so a cautious interpretation of "
            "the agent signals is applied."
        )
    elif risk_tolerance.upper() == "HIGH":
        guidance.append(
            "The user has a high risk tolerance and may accept greater market "
            "volatility, so momentum and sentiment signals are weighted more heavily."
        )
    else:
        guidance.append("The user has a moderate risk tolerance.")

    if portfolio_risk >= 70:
        warnings.append("Portfolio concentration is high; a single position dominates exposure.")

    if behavior_risk >= 70:
        warnings.append("Recent trading behavior indicates elevated turnover.")

    if market_signal.upper() == "BUY":
        if risk_tolerance.upper() == "LOW":
            guidance.append(
                "Although the synthesized signal leans bullish, the user's existing "
                "portfolio concentration and low risk tolerance warrant caution before acting."
            )
        else:
            guidance.append(
                "The bullish signal aligns with the user's risk profile, though "
                "position sizing should still respect the stated investment horizon."
            )
    elif market_signal.upper() == "SELL":
        guidance.append("The bearish signal suggests increased caution may be appropriate.")
    else:
        guidance.append("The signal is neutral, so monitoring rather than acting may be appropriate.")

    return {
        "risk_level": overall_risk_level,
        "guidance": guidance,
        "warnings": warnings,
    }
