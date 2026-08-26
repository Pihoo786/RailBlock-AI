from pathlib import Path
import sys

from fastapi import APIRouter, HTTPException

# Add project root so Python can find /optimizer
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from optimizer.engine import optimize_maintenance_block

from backend.app.schemas.optimizer_routes import OptimizeBlockRequest


router = APIRouter(
    prefix="/api/optimizer",
    tags=["Optimizer"]
)


@router.post("/recommend")
def recommend_block(
    data: OptimizeBlockRequest
):
    try:
        maintenance_job = {
            "job_id": data.job_id,
            "section": data.section,
            "duration_minutes": data.duration_minutes,
            "department": data.department,
            "priority": data.priority,
        }

        if data.risk_score is not None:
            maintenance_job["risk_score"] = data.risk_score

        trains = [
            train.model_dump()
            for train in data.trains
        ]

        result = optimize_maintenance_block(
            maintenance_job,
            trains,
            available_start=data.available_start,
            available_end=data.available_end,
            interval_minutes=data.interval_minutes,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )