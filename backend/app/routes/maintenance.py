from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Asset, MaintenanceRequest
from app.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestResponse,
)


router = APIRouter(
    prefix="/api/maintenance-requests",
    tags=["Maintenance Requests"],
)


@router.post(
    "/",
    response_model=MaintenanceRequestResponse,
    status_code=201,
)
def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Find asset using railway/business asset code
    # --------------------------------------------------------

    asset = (
        db.query(Asset)
        .filter(Asset.asset_code == request_data.asset_id)
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{request_data.asset_id}' not found",
        )

    # --------------------------------------------------------
    # 2. Validate section against asset when available
    # --------------------------------------------------------

    if asset.section_id and asset.section_id != request_data.section_id:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Asset '{request_data.asset_id}' does not belong "
                f"to section '{request_data.section_id}'"
            ),
        )

    # --------------------------------------------------------
    # 3. Generate public request ID
    # --------------------------------------------------------

    request_id = f"MR-{uuid4().hex[:8].upper()}"

    # --------------------------------------------------------
    # 4. Create maintenance request
    # --------------------------------------------------------

    maintenance_request = MaintenanceRequest(
        request_id=request_id,
        asset_id=asset.id,
        department=request_data.department.value,
        section_id=request_data.section_id,
        category=request_data.category,
        severity=request_data.severity,
        raw_text=request_data.raw_text,
        reported_at=request_data.reported_at,
        required_duration_minutes=request_data.required_duration_minutes,
        maintenance_type=request_data.maintenance_type,
        urgency_remarks=request_data.urgency_remarks,
        department_fields=request_data.department_fields,
        status="SUBMITTED",
    )

    db.add(maintenance_request)
    db.commit()
    db.refresh(maintenance_request)

    return maintenance_request


@router.get(
    "/",
    response_model=list[MaintenanceRequestResponse],
)
def get_maintenance_requests(
    db: Session = Depends(get_db),
):
    return db.query(MaintenanceRequest).all()