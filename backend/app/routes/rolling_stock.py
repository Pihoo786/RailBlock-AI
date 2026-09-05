from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Asset, RollingStockSchedule
from app.schemas.rolling_stock import (
    RollingStockAvailabilityResponse,
)


router = APIRouter(
    prefix="/api/rolling-stock",
    tags=["Rolling Stock"],
)


@router.get(
    "/availability",
    response_model=list[RollingStockAvailabilityResponse],
)
def get_rolling_stock_availability(
    section_id: str,
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Asset,
            RollingStockSchedule,
        )
        .join(
            RollingStockSchedule,
            RollingStockSchedule.asset_id == Asset.id,
        )
        .filter(
            Asset.section_id == section_id,
        )
        .all()
    )

    results = []

    for asset, schedule in rows:
        results.append(
            {
                "asset_id": asset.id,
                "asset_code": asset.asset_code,
                "asset_type": asset.asset_type,
                "section_id": asset.section_id,
                "shed_location": schedule.shed_location,
                "status": schedule.status,
                "overhaul_start": schedule.overhaul_start,
                "overhaul_end": schedule.overhaul_end,
            }
        )

    return results