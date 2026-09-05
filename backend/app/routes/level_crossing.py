from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import LCHazardEvent
from app.schemas.level_crossing import (
    LCHazardAlertCreate,
    LCHazardAlertResponse,
    LCRerouteRequest,
)
from app.services.alert_manager import alert_manager


router = APIRouter(
    prefix="/api/lc",
    tags=["Level Crossing"],
)


@router.post(
    "/hazard-alert",
    response_model=LCHazardAlertResponse,
    status_code=201,
)
async def create_hazard_alert(
    alert: LCHazardAlertCreate,
    db: Session = Depends(get_db),
):
    valid_hazard_types = {
        "OBSTACLE_DETECTED",
        "GATE_MALFUNCTION",
    }

    valid_severities = {
        "CRITICAL",
        "WARNING",
    }

    if alert.hazard_type not in valid_hazard_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid hazard_type",
        )

    if alert.severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail="Invalid severity",
        )

    event = LCHazardEvent(
        lc_id=alert.id,
        section_id=alert.section_id,
        hazard_type=alert.hazard_type,
        severity=alert.severity,
        detected_at=alert.detected_at,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    await alert_manager.broadcast(
        {
            "event": "LC_HAZARD_ALERT",
            "data": {
                "lc_id": event.lc_id,
                "section_id": event.section_id,
                "hazard_type": event.hazard_type,
                "severity": event.severity,
                "detected_at": event.detected_at.isoformat(),
            },
        }
    )

    return event


@router.post("/reroute-request")
async def create_reroute_request(
    request: LCRerouteRequest,
):
    return {
        "status": "REOPTIMIZATION_REQUESTED",
        "lc_id": request.lc_id,
        "section_id": request.section_id,
        "estimated_delay_minutes": (
            request.estimated_delay_minutes
        ),
        "message": (
            "Level crossing delay received. "
            "Downstream block re-optimization requested."
        ),
    }