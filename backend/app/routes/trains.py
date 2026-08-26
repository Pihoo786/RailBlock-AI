from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Train


router = APIRouter(
    prefix="/api/trains",
    tags=["Trains"]
)


@router.post("/")
def create_train(
    train_number: str,
    train_name: str,
    source: str,
    destination: str,
    section: str,
    entry_time: str,
    exit_time: str,
    db: Session = Depends(get_db)
):
    train = Train(
        train_number=train_number,
        train_name=train_name,
        source=source,
        destination=destination,
        section=section,
        entry_time=entry_time,
        exit_time=exit_time
    )

    db.add(train)
    db.commit()
    db.refresh(train)

    return {
        "id": train.id,
        "train_number": train.train_number,
        "train_name": train.train_name,
        "section": train.section,
        "entry_time": train.entry_time,
        "exit_time": train.exit_time
    }


@router.get("/")
def get_trains(
    db: Session = Depends(get_db)
):
    return db.query(Train).all()