from models import BehaviorData


def calculate_behavior_score(behavior):
    score = 0

    if behavior.trades_last_30_days >= 20:
        score += 40
    elif behavior.trades_last_30_days >= 10:
        score += 25
    else:
        score += 10

    if behavior.average_holding_days <= 7:
        score += 30
    elif behavior.average_holding_days <= 30:
        score += 20
    else:
        score += 10

    if behavior.portfolio_changes >= 10:
        score += 30
    elif behavior.portfolio_changes >= 5:
        score += 20
    else:
        score += 10

    return score


def get_behavior_level(score):

    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MODERATE"
    else:
        return "LOW"