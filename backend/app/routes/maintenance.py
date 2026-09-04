from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Asset,
    MaintenanceRequest,
    RiskScore,
    Section,
)
from app.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestResponse,
)
from app.services.ml_feature_builder import build_ml_features
from app.services.ml_service import predict_risk


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
    # 1. Find asset
    # --------------------------------------------------------

    asset = (
        db.query(Asset)
        .filter(
            Asset.asset_code == request_data.asset_id
        )
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail=f"Asset '{request_data.asset_id}' not found",
        )

    # --------------------------------------------------------
    # 2. Find section
    # --------------------------------------------------------

    section = (
        db.query(Section)
        .filter(
            Section.section_id == request_data.section_id
        )
        .first()
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Section '{request_data.section_id}' not found"
            ),
        )

    # --------------------------------------------------------
    # 3. Validate asset-section relationship
    # --------------------------------------------------------

    if (
        asset.section_id
        and asset.section_id != request_data.section_id
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Asset '{request_data.asset_id}' does not "
                f"belong to section '{request_data.section_id}'"
            ),
        )

    # --------------------------------------------------------
    # 4. Generate request ID
    # --------------------------------------------------------

    request_id = f"MR-{uuid4().hex[:8].upper()}"

    # --------------------------------------------------------
    # 5. Create maintenance request
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
        required_duration_minutes=(
            request_data.required_duration_minutes
        ),
        maintenance_type=request_data.maintenance_type,
        urgency_remarks=request_data.urgency_remarks,
        department_fields=request_data.department_fields,
        status="SUBMITTED",
    )

    db.add(maintenance_request)
    db.flush()

    # --------------------------------------------------------
    # 6. Build ML feature vector
    # --------------------------------------------------------

    ml_features = build_ml_features(
        db=db,
        maintenance_request=maintenance_request,
        asset=asset,
        section=section,
    )

    # --------------------------------------------------------
    # 7. Call ML risk service
    # --------------------------------------------------------

    try:
        risk_result = predict_risk(ml_features)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=(
                "ML risk service unavailable or failed: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # 8. Save ML result
    # --------------------------------------------------------

    risk_score = RiskScore(
        request_id=maintenance_request.id,
        failure_probability=(
            risk_result["failure_probability"]
        ),
        risk_band=risk_result["risk_band"],
        model_version=risk_result["model_version"],
        top_features=risk_result.get(
            "top_features",
            [],
        ),
    )

    db.add(risk_score)

    # --------------------------------------------------------
    # 9. Advance lifecycle
    # --------------------------------------------------------

    maintenance_request.status = "RISK_SCORED"

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