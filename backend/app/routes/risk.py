from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Asset
from app.schemas.risk import (
    RiskCalculateRequest,
    RiskResponse
)


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

    # Weighted risk calculation
    risk_score = (
        (1 - asset.condition_score) * 0.35
        + asset.criticality * 0.30
        + asset.overdue_score * 0.20
        + 0.15
    )

    # Keep score between 0 and 1
    risk_score = max(0, min(1, risk_score))

    if risk_score >= 0.75:
        priority = "HIGH"
    elif risk_score >= 0.50:
        priority = "MEDIUM"
    else:
        priority = "LOW"

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