from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Block, Train
from app.schemas.passenger import (
    PassengerBlockResponse,
    PassengerTrainResponse,
    PassengerBlocksResponse
)


router = APIRouter(
    prefix="/api/passenger",
    tags=["Passenger"]
)


# Passenger-visible statuses only
PASSENGER_VISIBLE_STATUSES = [
    "SCHEDULED",
    "APPROVED",
    "ACTIVE"
]


# ----------------------------------
# GET PASSENGER BLOCKS
# ----------------------------------

@router.get(
    "/blocks",
    response_model=list[PassengerBlocksResponse]
)
def get_passenger_blocks(
    db: Session = Depends(get_db)
):
    blocks = (
        db.query(Block)
        .filter(
            Block.status.in_(PASSENGER_VISIBLE_STATUSES)
        )
        .all()
    )

    return blocks


# ----------------------------------
# GET BLOCKS FOR ONE TRAIN
# ----------------------------------

@router.get(
    "/trains/{train_number}",
    response_model=PassengerTrainResponse
)
def get_passenger_train(
    train_number: str,
    db: Session = Depends(get_db)
):
    # Check whether train exists
    train = (
        db.query(Train)
        .filter(Train.train_number == train_number)
        .first()
    )

    if not train:
        raise HTTPException(
            status_code=404,
            detail="Train not found"
        )

    # Get passenger-visible blocks
    blocks = (
        db.query(Block)
        .filter(
            Block.train_number == train_number,
            Block.status.in_(PASSENGER_VISIBLE_STATUSES)
        )
        .all()
    )

    return {
        "train_number": train_number,
        "blocks": blocks
    }