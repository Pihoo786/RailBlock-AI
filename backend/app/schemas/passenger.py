from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PassengerBlockResponse(BaseModel):
    """Frozen public schema — intentionally contains no internal scoring fields."""

    model_config = ConfigDict(extra="forbid")

    train_number: str | None = None
    section: str
    start_time: datetime
    end_time: datetime
    expected_delay_minutes: int = Field(ge=0)
    reason: str
    reason_code: str
    status: str


class PassengerTrainResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    train_number: str
    blocks: list[PassengerBlockResponse]


class PassengerBlocksResponse(PassengerBlockResponse):
    pass
