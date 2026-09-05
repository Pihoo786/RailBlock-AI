"""Person 1 unified multi-asset risk and maintenance optimization engine.

This module is the stable integration facade for the RailBlock-AI prototype.
It combines explainable asset-risk scoring, traffic-safe window generation,
compatible co-planning, rolling-stock clustering, and the existing CP-SAT
planner into one JSON-serializable function.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .compatibility import are_compatible
from .cp_sat_optimizer import optimize_plan
from .priority_engine import priority_decision

ASSET_TYPES = {"TRACK", "CATENARY", "TRD", "LOCOMOTIVE", "COACH", "WAGON", "RACK", "RAKE"}
ASSET_TYPE_ALIASES = {"OHE": "CATENARY", "CARRIAGE": "COACH", "TRAIN": "RAKE"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bounded(value: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _num(value, default)))


def _norm_asset_type(value: Any) -> str:
    raw = str(value or "TRACK").upper().replace(" ", "_")
    return ASSET_TYPE_ALIASES.get(raw, raw)


def _age_risk(asset: dict[str, Any]) -> float:
    age = _num(asset.get("age_years", asset.get("age", 0)))
    expected = max(_num(asset.get("expected_life_years", 20)), 1.0)
    return _bounded(age / expected)


def _overdue_risk(asset: dict[str, Any]) -> float:
    overdue = max(0.0, _num(asset.get("days_overdue", 0)))
    cycle = max(_num(asset.get("maintenance_cycle_days", 90)), 1.0)
    return _bounded(overdue / cycle)


def _history_risk(asset: dict[str, Any]) -> float:
    """More repeated maintenance/failures increases risk; accepts either field."""
    failures = max(0.0, _num(asset.get("failure_count", 0)))
    maintenance = max(0.0, _num(asset.get("maintenance_history", asset.get("maintenance_count", 0))))
    return _bounded((0.7 * min(failures / 5.0, 1.0)) + (0.3 * min(maintenance / 10.0, 1.0)))


def calculate_multi_asset_risk(asset: dict[str, Any]) -> dict[str, Any]:
    """Calculate a transparent 0-1 risk score for track/TRD/rolling-stock assets.

    Factors: condition, age, overdue maintenance cycle, criticality, and
    maintenance/failure history. Explicit weights make the result easy to
    explain during a demo and tune later with historical data.
    """
    asset_type = _norm_asset_type(asset.get("asset_type", asset.get("type")))
    condition = asset.get("condition_score", asset.get("condition", 0.5))
    # A 1-5 condition scale is treated as risk when supplied; a 0-1 value is
    # treated directly as risk. This avoids breaking existing project data.
    condition_value = _num(condition, 0.5)
    condition_risk = condition_value / 5.0 if condition_value > 1 else condition_value
    criticality = asset.get("criticality", asset.get("criticality_score", 0.5))
    criticality_value = _num(criticality, 0.5)
    criticality_risk = criticality_value / 5.0 if criticality_value > 1 else criticality_value
    safety = _num(asset.get("safety_importance", asset.get("safety_criticality", 0.5)), 0.5)
    safety_risk = safety / 5.0 if safety > 1 else safety

    factors = {
        "condition_risk": round(_bounded(condition_risk), 3),
        "age_risk": round(_age_risk(asset), 3),
        "overdue_cycle_risk": round(_overdue_risk(asset), 3),
        "criticality_risk": round(_bounded(criticality_risk), 3),
        "history_risk": round(_history_risk(asset), 3),
        "safety_risk": round(_bounded(safety_risk), 3),
    }
    score = (
        0.25 * factors["condition_risk"]
        + 0.15 * factors["age_risk"]
        + 0.20 * factors["overdue_cycle_risk"]
        + 0.20 * factors["criticality_risk"]
        + 0.10 * factors["history_risk"]
        + 0.10 * factors["safety_risk"]
    )
    score = round(max(0.0, min(score, 1.0)), 3)
    band = "CRITICAL" if score >= 0.85 else "HIGH" if score >= 0.65 else "MEDIUM" if score >= 0.40 else "LOW"
    reasons = [name.replace("_", " ").title() for name, value in factors.items() if value >= 0.70]
    return {
        "asset_id": asset.get("asset_id"),
        "asset_type": asset_type,
        "risk_score": score,
        "risk_band": band,
        "risk_factors": factors,
        "risk_reasons": reasons or ["No individual risk factor crossed the high-risk threshold."],
    }


def _time_minutes(value: str) -> int:
    if value == "24:00":
        return 1440
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def _rolling_stock_match(block: dict[str, Any], stock: dict[str, Any]) -> bool:
    section = block.get("section")
    locations = {str(stock.get(k, "")) for k in ("section", "location", "shed", "depot", "home_shed")}
    same_area = str(section) in locations or not any(locations)
    due = bool(stock.get("overhaul_due", stock.get("maintenance_due", False)))
    due_date = stock.get("overhaul_due_date")
    if due_date:
        try:
            due = due or _time_minutes(block["start_time"]) >= _time_minutes(str(due_date)[-5:])
        except (ValueError, IndexError):
            pass
    status = str(stock.get("status", "AVAILABLE")).upper()
    available = status in {"AVAILABLE", "DUE", "SCHEDULED", "STABLED", "IDLE"}
    return same_area and due and available


def cluster_rolling_stock(blocks: Iterable[dict[str, Any]], rolling_stock: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Match overhaul-due locomotives/coaches/wagons/rakes to nearby blocks."""
    stock = list(rolling_stock)
    matches = []
    for block in blocks:
        matched = [item for item in stock if _rolling_stock_match(block, item)]
        if matched:
            matches.append({
                "block_id": block.get("candidate_id", block.get("block_id")),
                "section": block.get("section"),
                "start_time": block.get("start_time"),
                "end_time": block.get("end_time"),
                "matched_assets": [item.get("asset_id") for item in matched],
                "asset_types": sorted({_norm_asset_type(item.get("asset_type", item.get("type"))) for item in matched}),
                "count": len(matched),
            })
    return matches


def co_plan_requests(requests: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group requests that can safely share one section/time block."""
    groups: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for request in requests:
        key = (str(request["section"]), request.get("requested_date"))
        groups.setdefault(key, []).append(request)

    result = []
    for (section, requested_date), group in groups.items():
        compatible = all(
            are_compatible(a.get("block_type"), b.get("block_type"))
            for i, a in enumerate(group) for b in group[i + 1 :]
        )
        if not compatible or len(group) == 1:
            result.extend(dict(item) for item in group)
            continue
        lead = max(group, key=lambda item: _num(item.get("risk_score", 0)))
        merged = dict(lead)
        merged["request_id"] = "+".join(item["request_id"] for item in group)
        merged["source_request_ids"] = [item["request_id"] for item in group]
        merged["duration_minutes"] = max(int(item["duration_minutes"]) for item in group)
        merged["departments"] = sorted({item.get("department", "Engineering") for item in group})
        merged["asset_ids"] = [item.get("asset_id") for item in group]
        if requested_date:
            merged["requested_date"] = requested_date
        result.append(merged)
    return result


def optimize_multi_asset_plan(
    requests: Iterable[dict[str, Any]],
    trains: Iterable[dict[str, Any]],
    *,
    ml_outputs: Iterable[dict[str, Any]] = (),
    assets: Iterable[dict[str, Any]] = (),
    rolling_stock: Iterable[dict[str, Any]] = (),
    existing_blocks: Iterable[dict[str, Any]] = (),
    rejected_candidates: dict[str, list[str]] | None = None,
    available_start: str = "06:00",
    available_end: str = "22:00",
    interval_minutes: int = 30,
) -> dict[str, Any]:
    """Main Person 1 API. Returns JSON-safe optimized recommendations."""
    request_list = [dict(r) for r in requests]
    asset_map = {str(a.get("asset_id")): a for a in assets}
    risk_by_asset = {}
    for asset_id, asset in asset_map.items():
        risk_by_asset[asset_id] = calculate_multi_asset_risk(asset)

    for request in request_list:
        risk = risk_by_asset.get(str(request.get("asset_id")))
        if risk:
            request["risk_score"] = risk["risk_score"]
            request["priority"] = risk["risk_band"]
        else:
            request["risk_score"] = _bounded(request.get("risk_score", 0.5), 0.5)

    # Use the existing CP-SAT engine as the authoritative traffic/block solver.
    ml_list = [dict(item) for item in ml_outputs]
    ml_map = {str(item.get("request_id")): item for item in ml_list}
    for request in request_list:
        rid = str(request.get("request_id"))
        if rid not in ml_map:
            ml_map[rid] = {"request_id": rid, "failure_probability": request.get("risk_score", 0.5), "risk_band": request.get("priority", "MEDIUM")}
    plan = optimize_plan(
        request_list,
        list(ml_map.values()),
        list(trains),
        existing_blocks=existing_blocks,
        rejected_candidates=rejected_candidates,
        available_start=available_start,
        available_end=available_end,
        interval_minutes=interval_minutes,
    )
    matches = cluster_rolling_stock(plan["plan"], rolling_stock)

    return {
        "engine": "RailBlock-AI Person 1 Multi-Asset Optimization Engine",
        "engine_version": "1.0",
        "risk_assessments": list(risk_by_asset.values()),
        "priority_decisions": plan["priority_decisions"],
        "recommended_blocks": plan["plan"],
        "rolling_stock_matches": matches,
        "unscheduled_items": plan["unscheduled_items"],
        "optimization_summary": {
            "requests_received": len(request_list),
            "blocks_recommended": len(plan["plan"]),
            "requests_unscheduled": len(plan["unscheduled_items"]),
            "rolling_stock_matches": sum(item["count"] for item in matches),
            "solver": plan["solver"],
        },
    }


def optimize_engine(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Alias used by integrations that expect an ``optimization_engine`` facade."""
    return optimize_multi_asset_plan(*args, **kwargs)
