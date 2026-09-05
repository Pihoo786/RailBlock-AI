from __future__ import annotations

from datetime import datetime
from typing import Any

from optimizer.cp_sat_optimizer import recommend_single


def _enum_value(value: Any) -> str:
    """Return the underlying string value for Enum or plain string inputs."""
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _department_for_optimizer(value: Any) -> str:
    """
    Convert backend department enum values into the optimizer's
    human-readable department names.
    """
    value = _enum_value(value)

    mapping = {
        "ENGINEERING": "Engineering",
        "SIGNAL_TELECOM": "S&T",
        "TRACTION_DISTRIBUTION": "TRD",
    }

    return mapping.get(value, value)


def _block_type_for_optimizer(value: Any) -> str:
    """
    Convert the backend/API block type into the optimizer's
    internal representation.
    """
    value = _enum_value(value).upper()

    mapping = {
        "TRAFFIC_BLOCK": "TRAFFIC",
        "TRAFFIC": "TRAFFIC",
        "POWER_BLOCK": "POWER",
        "POWER": "POWER",
        "DISCONNECTION": "DISCONNECTION",
    }

    return mapping.get(value, "TRAFFIC")


def _block_type_from_optimizer(value: Any) -> str:
    """Convert optimizer block type back to the shared backend contract."""
    value = str(value).upper()

    mapping = {
        "TRAFFIC": "TRAFFIC_BLOCK",
        "POWER": "POWER_BLOCK",
        "DISCONNECTION": "DISCONNECTION",
    }

    return mapping.get(value, value)


def _calculate_days_overdue(
    last_maintenance_date: datetime | None,
    reported_at: datetime,
) -> int:
    """Calculate maintenance overdue duration for the priority engine."""
    if not last_maintenance_date:
        return 0

    if reported_at.tzinfo is not None:
        reported_at = reported_at.replace(tzinfo=None)

    if last_maintenance_date.tzinfo is not None:
        last_maintenance_date = last_maintenance_date.replace(tzinfo=None)

    delta = reported_at - last_maintenance_date
    return max(0, delta.days)


def _asset_criticality(asset: Any) -> float:
    """
    Convert the asset criticality representation into the optimizer's
    expected 0-1 value.
    """
    raw = getattr(asset, "criticality", None)

    if raw is None:
        raw = getattr(asset, "criticality_class", None)

    if isinstance(raw, (int, float)):
        return max(0.0, min(1.0, float(raw)))

    mapping = {
        "LOW": 0.25,
        "MEDIUM": 0.50,
        "HIGH": 0.75,
        "CRITICAL": 1.00,
    }

    return mapping.get(str(raw).upper(), 0.50)


def _operational_impact(asset: Any, section: Any) -> float:
    """
    Derive a normalized operational impact score.

    Prefer section traffic density when available because a maintenance
    block on a busier section has greater operational significance.
    """
    value = getattr(section, "traffic_density_gmt", None)

    if value is None:
        return 0.5

    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.5

    # Prototype normalization.
    # The optimizer itself only needs a bounded 0-1 value.
    return max(0.0, min(1.0, value))


def build_optimizer_request(
    maintenance_request: Any,
    asset: Any,
    section: Any,
) -> dict[str, Any]:
    """Convert SQLAlchemy objects into Person1 optimizer request format."""

    reported_at = maintenance_request.reported_at

    return {
        "request_id": maintenance_request.request_id,
        "asset_id": maintenance_request.asset_id,
        "department": _department_for_optimizer(
            maintenance_request.department
        ),
        "section": maintenance_request.section_id,
        "duration_minutes": maintenance_request.required_duration_minutes,
        "days_overdue": _calculate_days_overdue(
            getattr(asset, "last_maintenance_date", None),
            reported_at,
        ),
        "severity": (
            maintenance_request.final_severity
            or maintenance_request.severity
            or "MEDIUM"
        ),
        "asset_criticality": _asset_criticality(asset),
        "operational_impact": _operational_impact(asset, section),
        "block_type": _block_type_for_optimizer(
            getattr(maintenance_request, "block_type", "TRAFFIC_BLOCK")
        ),
        "status": maintenance_request.status,
    }


def build_optimizer_trains(
    train_rows: list[Any],
) -> list[dict[str, Any]]:
    """Convert train_schedule SQLAlchemy rows into optimizer train format."""

    trains: list[dict[str, Any]] = []

    for train in train_rows:
        trains.append(
            {
                "train_id": str(train.train_no),
                "section": train.section_id,
                "entry_time": train.entry_time.strftime("%H:%M"),
                "exit_time": train.exit_time.strftime("%H:%M"),
            }
        )

    return trains


def recommend_maintenance_block(
    maintenance_request: Any,
    asset: Any,
    section: Any,
    risk_score: Any,
    train_rows: list[Any],
) -> dict[str, Any]:
    """
    Run Person1 priority + candidate generation + CP-SAT optimization
    for one maintenance request.
    """

    request = build_optimizer_request(
        maintenance_request,
        asset,
        section,
    )

    trains = build_optimizer_trains(train_rows)

    ml_output = {
        "request_id": maintenance_request.request_id,
        "failure_probability": float(risk_score.failure_probability),
        "risk_band": risk_score.risk_band,
        "model_version": risk_score.model_version,
        "top_features": risk_score.top_features or [],
    }

    result = recommend_single(
        request,
        ml_output,
        trains,
    )

    recommended = result.get("recommended_block")

    if recommended:
        recommended = {
            **recommended,
            "block_type": _block_type_from_optimizer(
                recommended.get("block_type")
            ),
            "section_id": maintenance_request.section_id,
        }

    alternatives = []

    for candidate in result.get("alternatives", []):
        alternatives.append(
            {
                **candidate,
                "block_type": _block_type_from_optimizer(
                    candidate.get("block_type")
                ),
                "section_id": maintenance_request.section_id,
            }
        )

    return {
        "recommended_block": recommended,
        "alternatives": alternatives,
        "unscheduled_items": result.get("unscheduled_items", []),
        "priority": result["priority"],
    }