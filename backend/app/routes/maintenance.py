from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import MaintenanceJob
from app.schemas.maintenance import (
    MaintenanceJobCreate,
    MaintenanceJobResponse
)


router = APIRouter(
    prefix="/api/maintenance-jobs",
    tags=["Maintenance Jobs"]
)


@router.get("/", response_model=list[MaintenanceJobResponse])
def get_maintenance_jobs(
    db: Session = Depends(get_db)
):
    return db.query(MaintenanceJob).all()


@router.post("/", response_model=MaintenanceJobResponse)
def create_maintenance_job(
    job_data: MaintenanceJobCreate,
    db: Session = Depends(get_db)
):
    new_job = MaintenanceJob(
        **job_data.model_dump(),
        status="PENDING"
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job