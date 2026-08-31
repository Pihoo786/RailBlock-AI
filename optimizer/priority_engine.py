"""Explainable decision logic that turns ML risk output into work priority.

This module intentionally does not claim to be ML.  It consumes the ML
prediction and applies visible Railway operational rules on top of it.
"""

from __future__ import annotations

from typing import Any


SEVERITY_SCORES = {"LOW": 0.25, "MEDIUM": 0.55, "HIGH": 0.80, "CRITICAL": 1.00}


def _bounded(value: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return default


def priority_decision(request: dict[str, Any], ml_output: dict[str, Any]) -> dict[str, Any]:
    """Create an explainable priority score and reasons for one request.

    Weights are decision logic for this prototype, not a trained ML model.
    """
    failure_probability = _bounded(ml_output.get("failure_probability"))
    criticality = _bounded(request.get("asset_criticality", request.get("criticality", 0.5)))
    operational_impact = _bounded(request.get("operational_impact", 0.5))
    overdue = _bounded(float(request.get("days_overdue", 0)) / 90.0, 0.0)
    severity = SEVERITY_SCORES.get(str(request.get("severity", "MEDIUM")).upper(), 0.55)

    score = round(
        0.40 * failure_probability
        + 0.20 * criticality
        + 0.15 * operational_impact
        + 0.10 * overdue
        + 0.15 * severity,
        3,
    )
    if score >= 0.85:
        band = "CRITICAL"
    elif score >= 0.65:
        band = "HIGH"
    elif score >= 0.40:
        band = "MEDIUM"
    else:
        band = "LOW"

    reasons: list[str] = []
    if failure_probability >= 0.70:
        reasons.append(f"High predicted failure probability ({failure_probability:.0%}).")
    if criticality >= 0.70:
        reasons.append("Asset is operationally critical.")
    if overdue >= 0.50:
        reasons.append(f"Maintenance is {request.get('days_overdue', 0)} days overdue.")
    if severity >= 0.80:
        reasons.append(f"Safety severity is {request.get('severity', 'HIGH')}." )
    if not reasons:
        reasons.append("No high-risk factor crossed the escalation threshold.")

    return {
        "request_id": request["request_id"],
        "priority_score": score,
        "priority_band": band,
        "priority_reasons": reasons,
        "decision_logic": {
            "failure_probability": 0.40,
            "asset_criticality": 0.20,
            "operational_impact": 0.15,
            "days_overdue": 0.10,
            "severity": 0.15,
        },
        "ml_model_version": ml_output.get("model_version", "unknown"),
    }
