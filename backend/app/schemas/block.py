from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BlockCreate(BaseModel):
    train_number: str
    section: str
    start_time: datetime
    end_time: datetime
    departments: str
    affected_trains: int
    expected_delay_minutes: int
    reason: str


class BlockResponse(BaseModel):
    id: int
    train_number: str
    section: str
    start_time: datetime
    end_time: datetime
    departments: str
    affected_trains: int
    expected_delay_minutes: int
    reason: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class OptimizationResponse(BaseModel):
    optimization_result: dict[str, Any]
    saved_block: dict[str, Any]