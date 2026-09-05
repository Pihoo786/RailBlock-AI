from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Asset,
    Block,
    BlockConflict,
    MaintenanceRequest,
    RiskScore,
    Section,
    TrainSchedule,
)
from app.schemas.maintenance import (
    MaintenanceRequestCreate,
    MaintenanceRequestResponse,
)
from app.services.ml_feature_builder import build_ml_features
from app.services.ml_service import predict_risk

from app.services.optimizer_service import recommend_maintenance_block
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
    # 9. Save ML result
    # --------------------------------------------------------

    db.add(risk_score)
    db.flush()

    maintenance_request.status = "RISK_SCORED"

    # --------------------------------------------------------
    # 10. Get trains for this section
    # --------------------------------------------------------

# Get trains only for the maintenance request's planning date.
    planning_date = request_data.reported_at.date()
    day_start = datetime.combine(planning_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    train_rows = (
        db.query(TrainSchedule)
        .filter(
            TrainSchedule.section_id == request_data.section_id,
            TrainSchedule.entry_time >= day_start,
            TrainSchedule.entry_time < day_end,
        )
        .all()
    )

    # --------------------------------------------------------
    # 11. Run AI priority + CP-SAT optimizer
    # --------------------------------------------------------

    try:
        optimization_result = recommend_maintenance_block(
            maintenance_request=maintenance_request,
            asset=asset,
            section=section,
            risk_score=risk_score,
            train_rows=train_rows,
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=(
                "AI optimization service failed: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------------------------------
    # 12. Save recommended block
    # --------------------------------------------------------

    recommended = optimization_result.get(
        "recommended_block"
    )

    priority = optimization_result.get(
        "priority",
        {},
    )

    if recommended:

        start_time = datetime.fromisoformat(
            f"{request_data.reported_at.date()}T"
            f"{recommended['start_time']}:00"
        )

        end_time = datetime.fromisoformat(
            f"{request_data.reported_at.date()}T"
            f"{recommended['end_time']}:00"
        )

        departments = recommended.get(
            "departments",
            [],
        )

        block = Block(
            request_id=maintenance_request.id,
            train_number=None,
            section=recommended["section"],
            section_id=request_data.section_id,
            start_time=start_time,
            end_time=end_time,
            departments=",".join(
                str(department)
                for department in departments
            ),
            affected_trains=recommended.get(
                "affected_trains",
                0,
            ),
            expected_delay_minutes=recommended.get(
                "expected_disruption_minutes",
                0,
            ),
            reason=recommended.get(
                "explanation",
                "AI-optimized maintenance block.",
            ),
            status="RECOMMENDED",
            block_type=recommended.get(
                "block_type"
            ),
            priority_score=priority.get(
                "priority_score"
            ),
            priority_band=priority.get(
                "priority_band"
            ),
            priority_reasons=priority.get(
                "priority_reasons",
                [],
            ),
        )

        db.add(block)
        db.flush()

        # ----------------------------------------------------
        # 13. Save train conflicts, if optimizer returns any
        # ----------------------------------------------------

        for train_id in recommended.get(
            "affected_train_ids",
            [],
        ):
            conflict = BlockConflict(
                block_id=block.id,
                train_number=str(train_id),
                conflict_type="TRAIN_CONFLICT",
                conflict_reason=(
                    "Train occupies the section during "
                    "the proposed maintenance block."
                ),
                expected_delay_minutes=0,
            )

            db.add(conflict)

        maintenance_request.status = "RECOMMENDED"

    else:

        maintenance_request.status = "UNSCHEDULED"

    # --------------------------------------------------------
    # 14. Commit complete workflow
    # --------------------------------------------------------

    db.commit()
    db.refresh(maintenance_request)

    return maintenance_request