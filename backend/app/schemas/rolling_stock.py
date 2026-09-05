from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RollingStockAvailabilityResponse(BaseModel):
    asset_id: int
    asset_code: str
    asset_type: str
    section_id: str | None
    shed_location: str | None
    status: str
    overhaul_start: datetime | None
    overhaul_end: datetime | None

    model_config = ConfigDict(from_attributes=True)