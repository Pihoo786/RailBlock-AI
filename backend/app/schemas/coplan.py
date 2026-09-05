from pydantic import BaseModel


class CoPlanRequest(BaseModel):
    maintenance_request_ids: list[int]


class CoPlanResponse(BaseModel):
    request_ids: list[int]
    departments: list[str]
    section_id: str | None
    combined_duration_minutes: int
    recommendation: str