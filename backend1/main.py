from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

from models import UserProfile, Portfolio, BehaviorData



app = FastAPI(
    title="Risk & Personalization API",
    description="Hackathon prototype for personalized investment risk analysis",
    version="1.0"
)


# ==========================================
# REQUEST MODELS
# ==========================================

class BehaviorRequest(BaseModel):
    trades_last_30_days: int
    average_holding_days: int
    portfolio_changes: int


class MarketSignal(BaseModel):
    trend: str
    volatility: str
    momentum: str
    market_sentiment: str
    risk_factors: List[str]
    opportunities: List[str]
    confidence: float


class RiskAnalysisRequest(BaseModel):
    user_id: str
    risk_tolerance: str
    investment_goal: str
    investment_horizon: str

    portfolio: Dict[str, float]

    behavior: BehaviorRequest

    market_signal: MarketSignal


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def home():
    return {
        "status": "running",
        "service": "Risk & Personalization API"
    }


# ==========================================
# RISK ANALYSIS
# ==========================================

@app.post("/analyze")
def analyze(request: RiskAnalysisRequest):

    # Create user profile
    user = UserProfile(
        user_id=request.user_id,
        risk_tolerance=request.risk_tolerance,
        investment_goal=request.investment_goal,
        investment_horizon=request.investment_horizon
    )

    # Create portfolio
    portfolio = Portfolio(
        holdings=request.portfolio
    )

    # Create behavior data
    behavior = BehaviorData(
        trades_last_30_days=request.behavior.trades_last_30_days,
        average_holding_days=request.behavior.average_holding_days,
        portfolio_changes=request.behavior.portfolio_changes
    )

    # Convert market signal to dictionary
    market_signal = request.market_signal.model_dump()

    # Run risk analysis
    result = analyze_user(
        user,
        portfolio,
        behavior,
        market_signal
    )

    return result