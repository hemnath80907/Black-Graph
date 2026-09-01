from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from parp1 import app


# =========================================
# CREATE API
# =========================================

api = FastAPI(
    title="AI Financial Analysis API"
)


# =========================================
# ALLOW FRONTEND TO CONNECT
# =========================================

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# TEST ROUTE
# =========================================

@api.get("/")
def home():

    return {
        "message": "AI Financial Analysis API is running"
    }


# =========================================
# ANALYSIS ROUTE
# =========================================

@api.get("/analyze")
def analyze():

    # Prototype stock data
    stock_data = {

        # Technical
        "price": 1520,
        "sma20": 1480,
        "rsi": 63,
        "volume": 1500000,
        "avg_volume": 1000000,

        # Fundamental
        "revenue_growth": 15,
        "profit_growth": 18,
        "debt_ratio": 0.35,

        # Sentiment
        "positive_news": 8,
        "negative_news": 3,
        "sentiment_score": 0.7
    }


    # Run LangGraph
    result = app.invoke({
        "stock_data": stock_data
    })


    # Get results
    technical = result["technical_result"]
    fundamental = result["fundamental_result"]
    sentiment = result["sentiment_result"]
    synthesis = result["synthesis_result"]


    # Send JSON to frontend
    return {

        "technical": {
            "signal": technical["signal"],
            "confidence": technical["confidence"],
            "reasons": technical["reasons"]
        },

        "fundamental": {
            "signal": fundamental["signal"],
            "confidence": fundamental["confidence"],
            "reasons": fundamental["reasons"]
        },

        "sentiment": {
            "signal": sentiment["signal"],
            "confidence": sentiment["confidence"],
            "reasons": sentiment["reasons"]
        },

        "synthesis": {
            "final_signal": synthesis["final_signal"],
            "confidence": synthesis["confidence"],
            "agent_summary": synthesis["agent_summary"],
            "decision": synthesis["decision"]
        }
    }