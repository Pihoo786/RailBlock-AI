from pydantic import BaseModel, Field


class TrainScheduleInput(BaseModel):
    train_id: str
    section: str
    entry_time: str
    exit_time: str


class OptimizeBlockRequest(BaseModel):
    job_id: str
    section: str
    duration_minutes: int = Field(gt=0)
    department: str = "Engineering"
    priority: str = "MEDIUM"
    risk_score: float | None = None

    trains: list[TrainScheduleInput]

    available_start: str = "06:00"
    available_end: str = "22:00"
    interval_minutes: int = Field(default=30, gt=0)