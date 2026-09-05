from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Asset
from app.schemas.assets import AssetCreate, AssetResponse


router = APIRouter(
    prefix="/api/assets",
    tags=["Assets"]
)

@router.get("/", response_model=list[AssetResponse])
def get_assets(
    db: Session = Depends(get_db)
):
    assets = db.query(Asset).all()

    for asset in assets:
        if asset.condition_score is None:
            asset.condition_score = 0.0

        if asset.criticality is None:
            asset.criticality = 0.0

        if asset.overdue_score is None:
            asset.overdue_score = 0.0

    return assets

@router.post("/", response_model=AssetResponse)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db)
):
    new_asset = Asset(
        **asset_data.model_dump()
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset