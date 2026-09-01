from dataclasses import dataclass
from typing import Dict


@dataclass
class UserProfile:
    user_id: str
    risk_tolerance: str        # LOW | MODERATE | HIGH
    investment_goal: str
    investment_horizon: str


@dataclass
class Portfolio:
    holdings: Dict[str, float]  # symbol -> value


@dataclass
class BehaviorData:
    trades_last_30_days: int
    average_holding_days: int
    portfolio_changes: int
