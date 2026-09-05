from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import (
    Asset,
    Defect,
    MaintenanceRequest,
    Section,
    SignalFailure,
)


SEVERITY_RANK = {
    "ROUTINE": 0,
    "MINOR": 1,
    "MODERATE": 2,
    "SEVERE": 3,
    "URGENT": 4,
}

def days_between(start, end):
    if start is None or end is None:
        return 0

    # Normalize timezone-aware datetimes to naive UTC
    if start.tzinfo is not None:
        start = start.replace(tzinfo=None)

    if end.tzinfo is not None:
        end = end.replace(tzinfo=None)

    return max(
        0,
        int((end - start).total_seconds() / 86400),
    )

def build_ml_features(
    db: Session,
    maintenance_request: MaintenanceRequest,
    asset: Asset,
    section: Section,
) -> dict:
    requested_at = maintenance_request.reported_at

    # ---------------------------------------------------------
    # Asset age
    # ---------------------------------------------------------

    asset_age_days = days_between(
        asset.install_date,
        requested_at,
    )

    # ---------------------------------------------------------
    # Maintenance / USFD recency
    # ---------------------------------------------------------

    days_since_last_maintenance = days_between(
        asset.last_maintenance_date,
        requested_at,
    )

    days_since_usfd = None

    if asset.last_usfd_test_date is not None:
        days_since_usfd = days_between(
            asset.last_usfd_test_date,
            requested_at,
        )

    # ---------------------------------------------------------
    # Historical defects
    # ---------------------------------------------------------

    historical_defects = (
        db.query(Defect)
        .filter(
            Defect.asset_id == asset.id,
            Defect.reported_at < requested_at,
        )
        .all()
    )

    historical_defect_count = len(historical_defects)

    current_category = (
        maintenance_request.category
        or maintenance_request.nlp_category
        or ""
    ).strip().lower()

    repeated_defect_count = 0

    if current_category:
        repeated_defect_count = sum(
            1
            for defect in historical_defects
            if (defect.defect_category or "").strip().lower()
            == current_category
        )

    # ---------------------------------------------------------
    # Severity
    # ---------------------------------------------------------

    severity = (
        maintenance_request.final_severity
        or maintenance_request.nlp_severity
        or maintenance_request.severity
        or "ROUTINE"
    )

    severity_rank = SEVERITY_RANK.get(
        severity.upper(),
        0,
    )

    # ---------------------------------------------------------
    # Overdue
    # ---------------------------------------------------------

    days_overdue = 0.0

    # ---------------------------------------------------------
    # Signal failure history
    # ---------------------------------------------------------

    signal_failures = (
        db.query(SignalFailure)
        .filter(
            SignalFailure.asset_id == asset.id,
            SignalFailure.failure_timestamp < requested_at,
        )
        .all()
    )

    failure_frequency = None
    historical_downtime_minutes = None

    if signal_failures:
        failure_frequency = float(len(signal_failures))

        historical_downtime_minutes = float(
            sum(
                failure.downtime_minutes or 0
                for failure in signal_failures
            )
        )

    # ---------------------------------------------------------
    # TRD wire wear
    # ---------------------------------------------------------

    trd_wire_wear_flag = None

    if maintenance_request.department == "TRACTION_DISTRIBUTION":
        wire_categories = {
            "contact wire wear beyond limit",
            "ohe sag beyond tolerance",
            "dropper failure",
        }

        trd_wire_wear_flag = float(
            any(
                (defect.defect_category or "").strip().lower()
                in wire_categories
                for defect in historical_defects
            )
        )

    # ---------------------------------------------------------
    # Temporary block type for ML integration
    #
    # The scheduling/optimization layer will eventually
    # determine the actual block type.
    # ---------------------------------------------------------

    block_type = "Traffic Block"

    return {
        "request_id": maintenance_request.request_id,
        "asset_age_days": asset_age_days,
        "days_since_last_maintenance": days_since_last_maintenance,
        "days_since_usfd": days_since_usfd,
        "days_overdue": days_overdue,
        "historical_defect_count": float(
            historical_defect_count
        ),
        "repeated_defect_count": float(
            repeated_defect_count
        ),
        "severity_rank": float(severity_rank),
        "traffic_density_gmt": float(
            section.traffic_density_gmt or 0
        ),
        "track_geometry_index": (
            float(asset.track_geometry_index)
            if asset.track_geometry_index is not None
            else None
        ),
        "duration_minutes": float(
            maintenance_request.required_duration_minutes
        ),
        "train_count": float(
            section.train_count or 0
        ),
        "failure_frequency": failure_frequency,
        "historical_downtime_minutes": historical_downtime_minutes,
        "trd_wire_wear_flag": trd_wire_wear_flag,
        "asset_type": asset.asset_type,
        "department": maintenance_request.department,
        "criticality_class": (
            asset.criticality_class or "UNKNOWN"
        ),
        "block_type": block_type,
    }