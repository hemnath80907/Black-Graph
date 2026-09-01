from .models import UserProfile, Portfolio, BehaviorData
from .behavior import calculate_behavior_score
from .personalization import generate_personalized_guidance


def calculate_concentration(portfolio: Portfolio) -> float:
    total = sum(portfolio.holdings.values())
    if total == 0:
        return 0.0
    largest_holding = max(portfolio.holdings.values())
    return largest_holding / total


def calculate_portfolio_risk(portfolio: Portfolio) -> int:
    concentration = calculate_concentration(portfolio)
    if concentration >= 0.50:
        return 80
    elif concentration >= 0.35:
        return 60
    elif concentration >= 0.20:
        return 40
    else:
        return 20


def get_profile_risk(risk_tolerance: str) -> int:
    risk_scores = {"LOW": 70, "MODERATE": 50, "HIGH": 30}
    return risk_scores.get(risk_tolerance.upper(), 50)


def calculate_overall_risk(portfolio_risk, behavior_risk, profile_risk) -> int:
    score = portfolio_risk * 0.40 + behavior_risk * 0.30 + profile_risk * 0.30
    return round(score)


def get_overall_risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MODERATE"
    else:
        return "LOW"


# ---------------------------------------------------------------------------
# Agent weighting by risk tolerance.
#
# This is the mechanism that makes the multi-agent output demonstrably
# different for different user profiles on identical market inputs: the
# synthesis layer takes a weighted vote/average using these weights rather
# than a flat majority vote.
#
# LOW risk tolerance:      lean on fundamentals + regulatory grounding (RAG),
#                           discount short-term technical/sentiment noise.
# HIGH risk tolerance:     lean on technical momentum + sentiment,
#                           discount slow-moving fundamentals.
# MODERATE risk tolerance: balanced.
# ---------------------------------------------------------------------------

AGENT_WEIGHTS_BY_RISK_TOLERANCE = {
    "LOW": {
        "Technical Agent": 0.15,
        "Fundamental Agent": 0.35,
        "Sentiment Agent": 0.10,
        "RAG Agent": 0.40,
    },
    "MODERATE": {
        "Technical Agent": 0.25,
        "Fundamental Agent": 0.25,
        "Sentiment Agent": 0.25,
        "RAG Agent": 0.25,
    },
    "HIGH": {
        "Technical Agent": 0.40,
        "Fundamental Agent": 0.15,
        "Sentiment Agent": 0.30,
        "RAG Agent": 0.15,
    },
}


def get_agent_weights(risk_tolerance: str) -> dict:
    return AGENT_WEIGHTS_BY_RISK_TOLERANCE.get(
        risk_tolerance.upper(), AGENT_WEIGHTS_BY_RISK_TOLERANCE["MODERATE"]
    )


def analyze_user(user: UserProfile, portfolio: Portfolio, behavior: BehaviorData, market_signal: str) -> dict:
    portfolio_risk = calculate_portfolio_risk(portfolio)
    behavior_risk = calculate_behavior_score(behavior)
    profile_risk = get_profile_risk(user.risk_tolerance)

    overall_risk = calculate_overall_risk(portfolio_risk, behavior_risk, profile_risk)
    overall_level = get_overall_risk_level(overall_risk)

    personalized_result = generate_personalized_guidance(
        risk_tolerance=user.risk_tolerance,
        overall_risk_level=overall_level,
        portfolio_risk=portfolio_risk,
        behavior_risk=behavior_risk,
        market_signal=market_signal,
    )

    return {
        "user_id": user.user_id,
        "risk_tolerance": user.risk_tolerance,
        "portfolio_risk_score": portfolio_risk,
        "portfolio_concentration": round(calculate_concentration(portfolio), 3),
        "behavior_risk_score": behavior_risk,
        "profile_risk_score": profile_risk,
        "overall_risk_score": overall_risk,
        "overall_risk_level": overall_level,
        "agent_weights_applied": get_agent_weights(user.risk_tolerance),
        "personalization": personalized_result,
    }
