from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Asset,
    Block,
    TrainSchedule,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    active_blocks = (
        db.query(Block)
        .filter(Block.status == "ACTIVE")
        .count()
    )

    recommended_blocks = (
        db.query(Block)
        .filter(Block.status == "RECOMMENDED")
        .count()
    )

    active_trains = db.query(TrainSchedule).count()

    total_assets = db.query(Asset).count()

    critical_assets = (
        db.query(Asset)
        .filter(Asset.priority == "CRITICAL")
        .count()
    )

    return {
        "active_blocks": active_blocks,
        "recommended_blocks": recommended_blocks,
        "active_trains": active_trains,
        "total_assets": total_assets,
        "critical_assets": critical_assets,
    }