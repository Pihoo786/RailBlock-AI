from pydantic import BaseModel


class MaintenanceJobCreate(BaseModel):
    asset_id: int
    department: str
    section: str
    description: str | None = None
    duration_minutes: int
    priority: str | None = None


class MaintenanceJobResponse(BaseModel):
    id: int
    asset_id: int
    department: str
    section: str
    description: str | None
    duration_minutes: int
    priority: str | None
    status: str

    class Config:
        from_attributes = True