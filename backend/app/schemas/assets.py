from pydantic import BaseModel


class AssetCreate(BaseModel):
    asset_code: str
    asset_type: str
    section: str
    condition_score: float
    criticality: float
    overdue_score: float


class AssetResponse(BaseModel):
    id: int
    asset_code: str
    asset_type: str
    section: str
    condition_score: float
    criticality: float
    overdue_score: float
    risk_score: float | None
    priority: str | None

    class Config:
        from_attributes = True