from pydantic import BaseModel


class RiskCalculateRequest(BaseModel):
    asset_id: int


class RiskResponse(BaseModel):
    asset_id: int
    asset_code: str
    risk_score: float
    priority: str