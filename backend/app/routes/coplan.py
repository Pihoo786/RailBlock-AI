from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import MaintenanceRequest
from app.schemas.coplan import (
    CoPlanRequest,
    CoPlanResponse,
)


router = APIRouter(
    prefix="/api/blocks",
    tags=["Block Co-Planning"],
)


@router.post(
    "/co-plan",
    response_model=CoPlanResponse,
)
def co_plan_blocks(
    data: CoPlanRequest,
    db: Session = Depends(get_db),
):
    if not data.maintenance_request_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one maintenance request is required.",
        )

    requests = (
        db.query(MaintenanceRequest)
        .filter(
            MaintenanceRequest.id.in_(
                data.maintenance_request_ids
            )
        )
        .all()
    )

    if len(requests) != len(data.maintenance_request_ids):
        raise HTTPException(
            status_code=404,
            detail="One or more maintenance requests were not found.",
        )

    sections = {
        request.section_id
        for request in requests
    }

    if len(sections) != 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Co-planning currently requires all requests "
                "to belong to the same section."
            ),
        )

    departments = list(
        {
            str(request.department)
            for request in requests
        }
    )

    duration = max(
        request.required_duration_minutes or 0
        for request in requests
    )

    return {
        "request_ids": [
            request.id for request in requests
        ],
        "departments": departments,
        "section_id": requests[0].section_id,
        "combined_duration_minutes": duration,
        "recommendation": (
            "Requests can be considered for a shared "
            "maintenance block because they affect the "
            "same railway section."
        ),
    }