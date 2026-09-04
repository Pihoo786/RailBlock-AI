from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Department


class MaintenanceRequestCreate(BaseModel):
    asset_id: str = Field(..., min_length=1)
    department: Department
    section_id: str = Field(..., min_length=1)

    category: str | None = None

    severity: str = Field(..., min_length=1)

    raw_text: str = Field(..., min_length=1)

    reported_at: datetime

    required_duration_minutes: int = Field(..., gt=0)

    maintenance_type: str | None = None

    urgency_remarks: str | None = None

    department_fields: dict | None = None


class MaintenanceRequestResponse(BaseModel):
    id: int
    request_id: str
    status: str

    model_config = {
        "from_attributes": True
    }