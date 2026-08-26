from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Asset
from app.schemas.risk import RiskCalculateRequest, RiskResponse

from risk.ml_risk_module import calculate_risk_score, get_priority


router = APIRouter(
    prefix="/api/risk",
    tags=["Risk"]
)


@router.post(
    "/calculate",
    response_model=RiskResponse
)
def calculate_risk(
    risk_data: RiskCalculateRequest,
    db: Session = Depends(get_db)
):
    asset = db.get(Asset, risk_data.asset_id)

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    # Convert database asset into P2's risk engine format
    asset_data = {
        "asset_id": asset.asset_code,
        "condition_score": asset.condition_score,
        "criticality_score": asset.criticality,

        # Our DB already stores this as a normalized 0-1 score.
        # P2's module expects days, so convert it to a 0-100 scale.
        "days_overdue": asset.overdue_score * 100,

        # Not currently stored in our Asset table
        "maintenance_history": 0,
        "safety_importance": 3.0
    }

    risk_score = calculate_risk_score(asset_data)
    priority = get_priority(risk_score)

    asset.risk_score = risk_score
    asset.priority = priority

    db.commit()
    db.refresh(asset)

    return {
        "asset_id": asset.id,
        "asset_code": asset.asset_code,
        "risk_score": round(risk_score, 2),
        "priority": priority
    }