from models import UserProfile, Portfolio, BehaviorData
from behavior import calculate_behavior_score
from personalization import generate_personalized_guidance


def calculate_concentration(portfolio):
    total = sum(portfolio.holdings.values())

    if total == 0:
        return 0

    largest_holding = max(portfolio.holdings.values())

    return largest_holding / total


def calculate_portfolio_risk(portfolio):
    concentration = calculate_concentration(portfolio)

    if concentration >= 0.50:
        return 80
    elif concentration >= 0.35:
        return 60
    elif concentration >= 0.20:
        return 40
    else:
        return 20


def get_profile_risk(risk_tolerance):

    risk_scores = {
        "LOW": 70,
        "MODERATE": 50,
        "HIGH": 30
    }

    return risk_scores.get(risk_tolerance.upper(), 50)


def calculate_overall_risk(
    portfolio_risk,
    behavior_risk,
    profile_risk
):

    score = (
        portfolio_risk * 0.40
        + behavior_risk * 0.30
        + profile_risk * 0.30
    )

    return round(score)


def get_overall_risk_level(score):

    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MODERATE"
    else:
        return "LOW"


def analyze_user(user, portfolio, behavior, market_signal):

    # Portfolio risk
    portfolio_risk = calculate_portfolio_risk(portfolio)

    # Behavioral risk
    behavior_risk = calculate_behavior_score(behavior)

    # User profile risk
    profile_risk = get_profile_risk(
        user.risk_tolerance
    )

    # Overall risk
    overall_risk = calculate_overall_risk(
        portfolio_risk,
        behavior_risk,
        profile_risk
    )

    overall_level = get_overall_risk_level(
        overall_risk
    )

    # Personalization
    personalized_result = generate_personalized_guidance(
        risk_tolerance=user.risk_tolerance,
        overall_risk_level=overall_level,
        portfolio_risk=portfolio_risk,
        behavior_risk=behavior_risk,
        market_signal=market_signal
    )

    return {
        "user_id": user.user_id,
        "risk_tolerance": user.risk_tolerance,
        "portfolio_risk": portfolio_risk,
        "behavior_risk": behavior_risk,
        "profile_risk": profile_risk,
        "overall_risk_score": overall_risk,
        "overall_risk_level": overall_level,
        "personalization": personalized_result
    }


# =================================
# TEST
# =================================

# =================================
# PERSONALIZATION DEMO
# =================================

# Same market signal for both users
market_signal = "BULLISH"


# ---------------------------------
# USER 1 - CONSERVATIVE
# ---------------------------------

user1 = UserProfile(
    user_id="U001",
    risk_tolerance="LOW",
    investment_goal="LONG_TERM_GROWTH",
    investment_horizon="LONG_TERM"
)

portfolio1 = Portfolio(
    holdings={
        "RELIANCE": 50,
        "TCS": 30,
        "INFY": 20
    }
)

behavior1 = BehaviorData(
    trades_last_30_days=5,
    average_holding_days=120,
    portfolio_changes=2
)


result1 = analyze_user(
    user1,
    portfolio1,
    behavior1,
    market_signal
)


# ---------------------------------
# USER 2 - AGGRESSIVE
# ---------------------------------

user2 = UserProfile(
    user_id="U002",
    risk_tolerance="HIGH",
    investment_goal="SHORT_TERM_GROWTH",
    investment_horizon="SHORT_TERM"
)

portfolio2 = Portfolio(
    holdings={
        "RELIANCE": 20,
        "TCS": 30,
        "INFY": 25,
        "HDFC": 25
    }
)

behavior2 = BehaviorData(
    trades_last_30_days=20,
    average_holding_days=5,
    portfolio_changes=10
)


result2 = analyze_user(
    user2,
    portfolio2,
    behavior2,
    market_signal
)


# =================================
# DISPLAY RESULTS
# =================================

print("\n\n========================================")
print("       PERSONALIZATION DEMO")
print("========================================")

print("\nMARKET SIGNAL")
print("Symbol: RELIANCE")
print("Signal:", market_signal)
print("Confidence: 82%")


print("\n\n----------- USER 1 -----------")

print("User:", result1["user_id"])
print("Risk Tolerance:", result1["risk_tolerance"])
print("Overall Risk Score:", result1["overall_risk_score"])
print("Overall Risk Level:", result1["overall_risk_level"])

print("\nGuidance:")

for item in result1["personalization"]["guidance"]:
    print("-", item)

print("\nWarnings:")

for item in result1["personalization"]["warnings"]:
    print("-", item)


print("\n\n----------- USER 2 -----------")

print("User:", result2["user_id"])
print("Risk Tolerance:", result2["risk_tolerance"])
print("Overall Risk Score:", result2["overall_risk_score"])
print("Overall Risk Level:", result2["overall_risk_level"])

print("\nGuidance:")

for item in result2["personalization"]["guidance"]:
    print("-", item)

print("\nWarnings:")

for item in result2["personalization"]["warnings"]:
    print("-", item)


print("\n========================================")