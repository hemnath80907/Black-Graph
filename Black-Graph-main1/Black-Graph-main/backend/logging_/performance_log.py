"""
Performance & session log.

Captures, per analysis session:
  1. agent_response_latency_ms   (per agent + total) — system performance metric
  2. signal_accuracy_proxy       (did the synthesized signal's direction match
                                   the recorded 30-day forward return sign?) —
                                   research quality metric
  3. portfolio_risk_concentration (from the user's risk engine output)       —
                                   personalization / suitability metric
  4. degraded_agent_count        — reliability metric (bonus, beyond the
                                   minimum three required)

Uses SQLite (stdlib) so there is zero extra dependency for a hackathon judge
to install.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "sessions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    ts REAL NOT NULL,
    symbol TEXT NOT NULL,
    user_id TEXT NOT NULL,
    scenario TEXT NOT NULL,
    final_signal TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    forward_return_pct REAL,
    signal_accuracy_proxy INTEGER,
    portfolio_risk_concentration REAL,
    degraded_agent_count INTEGER NOT NULL,
    total_latency_ms REAL NOT NULL,
    latency_breakdown_json TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def _signal_accuracy_proxy(final_signal: str, forward_return_pct: Optional[float]) -> Optional[int]:
    """1 if the signal's implied direction matches the realized forward
    return's sign, 0 if not, None if HOLD (direction-neutral) or unknown."""
    if forward_return_pct is None or final_signal == "HOLD":
        return None
    predicted_up = final_signal == "BUY"
    actual_up = forward_return_pct > 0
    return int(predicted_up == actual_up)


def log_session(
    symbol: str,
    user_id: str,
    scenario: str,
    synthesis_result: dict,
    latency_ms: dict,
    forward_return_pct: Optional[float],
    portfolio_risk_concentration: Optional[float],
) -> dict:
    session_id = str(uuid.uuid4())[:8]
    accuracy_proxy = _signal_accuracy_proxy(synthesis_result["final_signal"], forward_return_pct)
    total_latency = round(sum(latency_ms.values()), 2)

    row = {
        "session_id": session_id,
        "ts": time.time(),
        "symbol": symbol,
        "user_id": user_id,
        "scenario": scenario,
        "final_signal": synthesis_result["final_signal"],
        "confidence": synthesis_result["confidence"],
        "forward_return_pct": forward_return_pct,
        "signal_accuracy_proxy": accuracy_proxy,
        "portfolio_risk_concentration": portfolio_risk_concentration,
        "degraded_agent_count": len(synthesis_result.get("degraded_agents", [])),
        "total_latency_ms": total_latency,
        "latency_breakdown_json": json.dumps(latency_ms),
    }

    with _connect() as conn:
        conn.execute(
            """INSERT INTO sessions
               (session_id, ts, symbol, user_id, scenario, final_signal, confidence,
                forward_return_pct, signal_accuracy_proxy, portfolio_risk_concentration,
                degraded_agent_count, total_latency_ms, latency_breakdown_json)
               VALUES (:session_id, :ts, :symbol, :user_id, :scenario, :final_signal, :confidence,
                       :forward_return_pct, :signal_accuracy_proxy, :portfolio_risk_concentration,
                       :degraded_agent_count, :total_latency_ms, :latency_breakdown_json)""",
            row,
        )

    return row


def get_recent_sessions(limit: int = 25) -> list[dict]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_aggregate_metrics() -> dict:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        total = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
        if total == 0:
            return {"sessions_logged": 0}

        avg_latency = conn.execute(
            "SELECT AVG(total_latency_ms) AS v FROM sessions"
        ).fetchone()["v"]

        accuracy_rows = conn.execute(
            "SELECT AVG(signal_accuracy_proxy) AS v FROM sessions WHERE signal_accuracy_proxy IS NOT NULL"
        ).fetchone()["v"]

        avg_concentration = conn.execute(
            "SELECT AVG(portfolio_risk_concentration) AS v FROM sessions "
            "WHERE portfolio_risk_concentration IS NOT NULL"
        ).fetchone()["v"]

        degraded_sessions = conn.execute(
            "SELECT COUNT(*) AS c FROM sessions WHERE degraded_agent_count > 0"
        ).fetchone()["c"]

        return {
            "sessions_logged": total,
            "avg_total_latency_ms": round(avg_latency, 2) if avg_latency is not None else None,
            "signal_accuracy_proxy_rate": round(accuracy_rows, 3) if accuracy_rows is not None else None,
            "avg_portfolio_risk_concentration": round(avg_concentration, 3) if avg_concentration is not None else None,
            "sessions_with_degraded_agents": degraded_sessions,
        }
