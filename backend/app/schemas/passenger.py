from datetime import datetime

from pydantic import BaseModel


class PassengerBlockResponse(BaseModel):
    section: str
    start_time: datetime
    end_time: datetime
    expected_delay_minutes: int
    reason: str
    status: str


class PassengerTrainResponse(BaseModel):
    train_number: str
    blocks: list[PassengerBlockResponse]


class PassengerBlocksResponse(BaseModel):
    train_number: str
    section: str
    start_time: datetime
    end_time: datetime
    expected_delay_minutes: int
    reason: str
    status: str