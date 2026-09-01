def generate_personalized_guidance(
    risk_tolerance,
    overall_risk_level,
    portfolio_risk,
    behavior_risk,
    market_signal
):
    guidance = []
    warnings = []

    if risk_tolerance.upper() == "LOW":
        guidance.append(
            "The user has a low risk tolerance, so a cautious "
            "interpretation is appropriate."
        )

    elif risk_tolerance.upper() == "HIGH":
        guidance.append(
            "The user has a high risk tolerance and may accept "
            "greater market volatility."
        )

    else:
        guidance.append(
            "The user has a moderate risk tolerance."
        )

    if portfolio_risk >= 70:
        warnings.append(
            "Portfolio concentration is high."
        )

    if behavior_risk >= 70:
        warnings.append(
            "Trading behavior indicates higher activity."
        )

    if market_signal.upper() == "BULLISH":

        if risk_tolerance.upper() == "LOW":
            guidance.append(
                "Although the market signal is bullish, "
                "the user should consider the existing portfolio risk."
            )

        else:
            guidance.append(
                "The bullish signal may be relevant to the user's "
                "investment profile, but market uncertainty remains."
            )

    elif market_signal.upper() == "BEARISH":

        guidance.append(
            "The bearish signal suggests increased caution "
            "may be appropriate."
        )

    else:

        guidance.append(
            "The market signal is neutral, so monitoring may "
            "be appropriate."
        )

    return {
        "risk_level": overall_risk_level,
        "guidance": guidance,
        "warnings": warnings
    }