from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from techp import technical_agent
from fundp import fundamental_agent
from sentp import sentiment_agent
from synp import synthesis_agent


# =========================================
# STATE
# =========================================

class AgentState(TypedDict, total=False):

    stock_data: dict

    technical_result: dict
    fundamental_result: dict
    sentiment_result: dict

    synthesis_result: dict


# =========================================
# TECHNICAL
# =========================================

def technical_node(state):

    print("Technical Agent running...")

    result = technical_agent(
        state["stock_data"]
    )

    return {
        "technical_result": result
    }


# =========================================
# FUNDAMENTAL
# =========================================

def fundamental_node(state):

    print("Fundamental Agent running...")

    result = fundamental_agent(
        state["stock_data"]
    )

    return {
        "fundamental_result": result
    }


# =========================================
# SENTIMENT
# =========================================

def sentiment_node(state):

    print("Sentiment Agent running...")

    result = sentiment_agent(
        state["stock_data"]
    )

    return {
        "sentiment_result": result
    }


# =========================================
# SYNTHESIS
# =========================================

def synthesis_node(state):

    print("\nSynthesis Agent running...")

    result = synthesis_agent(
        state["technical_result"],
        state["fundamental_result"],
        state["sentiment_result"]
    )

    print("Synthesis completed!")

    return {
        "synthesis_result": result
    }


# =========================================
# BUILD GRAPH
# =========================================

builder = StateGraph(AgentState)

builder.add_node(
    "technical",
    technical_node
)

builder.add_node(
    "fundamental",
    fundamental_node
)

builder.add_node(
    "sentiment",
    sentiment_node
)

builder.add_node(
    "synthesis",
    synthesis_node
)


# =========================================
# PARALLEL
# =========================================

builder.add_edge(
    START,
    "technical"
)

builder.add_edge(
    START,
    "fundamental"
)

builder.add_edge(
    START,
    "sentiment"
)


# =========================================
# TO SYNTHESIS
# =========================================

builder.add_edge(
    "technical",
    "synthesis"
)

builder.add_edge(
    "fundamental",
    "synthesis"
)

builder.add_edge(
    "sentiment",
    "synthesis"
)


# =========================================
# END
# =========================================

builder.add_edge(
    "synthesis",
    END
)


app = builder.compile()


# =========================================
# SAMPLE DATA
# =========================================

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


# =========================================
# RUN
# =========================================

print("\n==============================")
print(" MULTI AGENT SYSTEM")
print("==============================\n")

result = app.invoke({
    "stock_data": stock_data
})


# =========================================
# FINAL OUTPUT
# =========================================

print("\n==============================")
print(" FINAL SYNTHESIS")
print("==============================")

final_result = result["synthesis_result"]

print(
    "\nFinal Signal:",
    final_result["final_signal"]
)

print(
    "Confidence:",
    final_result["confidence"],
    "%"
)

print("\nAgent Results:")

print(
    "Technical:",
    final_result["agent_summary"]["technical"]
)

print(
    "Fundamental:",
    final_result["agent_summary"]["fundamental"]
)

print(
    "Sentiment:",
    final_result["agent_summary"]["sentiment"]
)

print("\nDecision:")

print(
    final_result["decision"]
)

print("\n==============================")
print(" SYSTEM COMPLETED")
print("==============================")