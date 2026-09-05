from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LCHazardAlertCreate(BaseModel):
    id: str
    section_id: str
    hazard_type: str
    detected_at: datetime
    severity: str


class LCHazardAlertResponse(BaseModel):
    id: int
    lc_id: str
    section_id: str
    hazard_type: str
    severity: str
    detected_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LCRerouteRequest(BaseModel):
    lc_id: str
    section_id: str
    estimated_delay_minutes: int