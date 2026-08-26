from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Block
from app.schemas.block import BlockCreate, BlockResponse, OptimizationResponse

from datetime import datetime

from app.models.models import Block, MaintenanceJob, Asset, Train
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from optimizer.engine import optimize_maintenance_block

router = APIRouter(
    prefix="/api/blocks",
    tags=["Blocks"]
)


@router.post("/", response_model=BlockResponse)
def create_block(
    block_data: BlockCreate,
    db: Session = Depends(get_db)
):
    new_block = Block(
        **block_data.model_dump(),
        status="RECOMMENDED"
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block


@router.get("/", response_model=list[BlockResponse])
def get_blocks(
    db: Session = Depends(get_db)
):
    return db.query(Block).all()


@router.get("/{block_id}", response_model=BlockResponse)
def get_block(
    block_id: int,
    db: Session = Depends(get_db)
):
    block = db.get(Block, block_id)

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    return block


@router.post("/{block_id}/approve")
def approve_block(
    block_id: int,
    db: Session = Depends(get_db)
):
    block = db.get(Block, block_id)

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    block.status = "APPROVED"

    db.commit()
    db.refresh(block)

    return {
        "message": "Block approved successfully",
        "block_id": block.id,
        "status": block.status
    }


@router.post("/{block_id}/reject")
def reject_block(
    block_id: int,
    db: Session = Depends(get_db)
):
    block = db.get(Block, block_id)

    if not block:
        raise HTTPException(
            status_code=404,
            detail="Block not found"
        )

    block.status = "REJECTED"

    db.commit()
    db.refresh(block)

    return {
        "message": "Block rejected successfully",
        "block_id": block.id,
        "status": block.status
    }

@router.post("/optimize/{job_id}", response_model=OptimizationResponse)
def optimize_block(
    job_id: int,
    db: Session = Depends(get_db)
):
    # 1. Get maintenance job
    job = db.get(MaintenanceJob, job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Maintenance job not found"
        )

    # 2. Get the related asset for risk score
    asset = db.get(Asset, job.asset_id)

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Related asset not found"
        )

    # 3. Get trains on the same section
    trains = (
        db.query(Train)
        .filter(Train.section == job.section)
        .all()
    )

    # 4. Convert database trains into optimizer format
    optimizer_trains = [
        {
            "train_id": train.train_number,
            "section": train.section,
            "entry_time": train.entry_time,
            "exit_time": train.exit_time
        }
        for train in trains
    ]

    # 5. Prepare maintenance job for Person 1's optimizer
    optimizer_job = {
        "job_id": str(job.id),
        "section": job.section,
        "duration_minutes": job.duration_minutes,
        "department": job.department,
        "priority": job.priority or asset.priority or "MEDIUM",
        "risk_score": asset.risk_score
        if asset.risk_score is not None
        else 0.60
    }

    # 6. Run optimizer
    result = optimize_maintenance_block(
        optimizer_job,
        optimizer_trains
    )

    # Create a new optimized block
    new_block = Block(
        train_number=(
            result["affected_train_ids"][0]
            if result["affected_train_ids"]
            else "NO_CONFLICT"
        ),
        section=result["section"],
        start_time=datetime.strptime(
            result["start_time"],
            "%H:%M"
        ),
        end_time=datetime.strptime(
            result["end_time"],
            "%H:%M"
        ),
        departments=", ".join(
            result["departments"]
        ),
        affected_trains=result["affected_trains"],
        expected_delay_minutes=result["estimated_impact_minutes"],
        reason=f"Optimized maintenance block for job {job.id}",
        status=result["status"]
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return {
        "optimization_result": result,
        "saved_block": {
            "id": new_block.id,
            "section": new_block.section,
            "start_time": new_block.start_time,
            "end_time": new_block.end_time,
            "status": new_block.status
        }
    }

    # 7. Convert HH:MM strings to datetime
    start_time = datetime.strptime(
        result["start_time"],
        "%H:%M"
    )

    end_time = datetime.strptime(
        result["end_time"],
        "%H:%M"
    )

    # 8. Create and save the recommended block
    new_block = Block(
        train_number=(
            result["affected_train_ids"][0]
            if result["affected_train_ids"]
            else "ALL"
        ),
        section=result["section"],
        start_time=start_time,
        end_time=end_time,
        departments=", ".join(result["departments"]),
        affected_trains=result["affected_trains"],
        expected_delay_minutes=result[
            "estimated_impact_minutes"
        ],
        reason=(
            f"AI-recommended maintenance block for "
            f"job {job.id}. "
            f"Priority: {result['priority']}. "
            f"Risk score: {result['risk_score']}."
        ),
        status="RECOMMENDED"
    )

    db.add(new_block)

    # Update maintenance job status
    job.status = "OPTIMIZED"

    db.commit()
    db.refresh(new_block)

    return new_block