from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Block, Train
from app.schemas.passenger import (
    PassengerTrainResponse,
    PassengerBlocksResponse,
)
from app.services.passenger_service import PUBLIC_STATUSES, sanitize_block


router = APIRouter(prefix="/api/passenger", tags=["Passenger"])


@router.get("/blocks", response_model=list[PassengerBlocksResponse])
def get_passenger_blocks(db: Session = Depends(get_db)):
    """Return only passenger-safe, approved/public block information."""
    blocks = (
        db.query(Block)
        .filter(Block.status.in_(sorted(PUBLIC_STATUSES)))
        .all()
    )
    return [sanitize_block(block) for block in blocks]


@router.get("/trains/{train_number}", response_model=PassengerTrainResponse)
def get_passenger_train(
    train_number: str,
    db: Session = Depends(get_db),
):
    train = (
        db.query(Train)
        .filter(Train.train_number == train_number)
        .first()
    )

    if not train:
        raise HTTPException(status_code=404, detail="Train not found")

    blocks = (
        db.query(Block)
        .filter(
            Block.train_number == train_number,
            Block.status.in_(sorted(PUBLIC_STATUSES)),
        )
        .all()
    )

    return {
        "train_number": train_number,
        "blocks": [sanitize_block(block) for block in blocks],
    }
