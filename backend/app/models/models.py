from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# ============================================================
# USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    role: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    department: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# SECTIONS
# ============================================================

class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)

    section_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )

    from_station: Mapped[str] = mapped_column(
        String(150)
    )

    to_station: Mapped[str] = mapped_column(
        String(150)
    )

    zone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    traffic_density_gmt: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    train_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )


# ============================================================
# ASSETS
# Existing table preserved, MVP fields added
# ============================================================

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Railway/business asset identifier
    asset_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    asset_type: Mapped[str] = mapped_column(
        String(100)
    )

    # Existing field
    section: Mapped[str] = mapped_column(
        String(100)
    )

    # New canonical section identifier
    section_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    # Existing fields kept for compatibility
    condition_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    criticality: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    overdue_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    # ========================================================
    # ML FEATURE SOURCE FIELDS
    # ========================================================

    install_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    last_maintenance_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    last_usfd_test_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    criticality_class: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    traffic_density_gmt: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    track_geometry_index: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    # ========================================================
    # ML OUTPUT
    # ========================================================

    risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )


# ============================================================
# DEFECTS
# ============================================================

class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(primary_key=True)

    defect_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        index=True
    )

    source_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    defect_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    severity_text: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    free_text_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    reported_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

# ============================================================
# SIGNAL FAILURES
# Historical S&T failure data used by ML
# ============================================================

class SignalFailure(Base):
    __tablename__ = "signal_failures"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        index=True
    )

    failure_timestamp: Mapped[datetime] = mapped_column(
        DateTime
    )

    failure_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    restoration_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    downtime_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    restored_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
# ============================================================
# MAINTENANCE REQUESTS
# New canonical MVP request entity
# ============================================================

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        index=True
    )

    department: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    section_id: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    # Department-provided category
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # NLP-extracted category
    nlp_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    # Department-provided severity
    severity: Mapped[str] = mapped_column(
        String(20)
    )

    # NLP-derived severity
    nlp_severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Final safety-first severity
    final_severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    raw_text: Mapped[str] = mapped_column(
        Text
    )

    reported_at: Mapped[datetime] = mapped_column(
        DateTime
    )

    required_duration_minutes: Mapped[int] = mapped_column(
        Integer
    )

    maintenance_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    urgency_remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Department-specific fields
    department_fields: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    # ML/AI generated information
    status: Mapped[str] = mapped_column(
        String(30),
        default="SUBMITTED",
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# RISK SCORES
# Stores ML prediction separately from request
# ============================================================

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(primary_key=True)

    request_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_requests.id"),
        index=True
    )

    failure_probability: Mapped[float] = mapped_column(
        Float
    )

    risk_band: Mapped[str] = mapped_column(
        String(20)
    )

    model_version: Mapped[str] = mapped_column(
        String(50)
    )

    top_features: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    scored_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# TRAIN SCHEDULE
# Public timetable / occupancy data
# ============================================================

class TrainSchedule(Base):
    __tablename__ = "train_schedule"

    id: Mapped[int] = mapped_column(primary_key=True)

    train_no: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    train_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    train_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    section_id: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    from_station: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    to_station: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    entry_time: Mapped[datetime] = mapped_column(
        DateTime
    )

    exit_time: Mapped[datetime] = mapped_column(
        DateTime
    )


# ============================================================
# BLOCKS
# Existing table preserved + MVP fields
# ============================================================

class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Associated maintenance request
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("maintenance_requests.id"),
        nullable=True,
        index=True
    )

    train_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    section: Mapped[str] = mapped_column(
        String(100)
    )

    section_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime
    )

    departments: Mapped[str] = mapped_column(
        String(200)
    )

    # Existing field kept compatible
    affected_trains: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    expected_delay_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    reason: Mapped[str] = mapped_column(
        Text
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="RECOMMENDED",
        index=True
    )

    block_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    priority_band: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    priority_reasons: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True
    )

    optimization_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# BLOCK CONFLICTS
# ============================================================

class BlockConflict(Base):
    __tablename__ = "block_conflicts"

    id: Mapped[int] = mapped_column(primary_key=True)

    block_id: Mapped[int] = mapped_column(
        ForeignKey("blocks.id"),
        index=True
    )

    train_number: Mapped[str] = mapped_column(
        String(50),
        index=True
    )

    conflict_type: Mapped[str] = mapped_column(
        String(100)
    )

    conflict_reason: Mapped[str] = mapped_column(
        Text
    )

    expected_delay_minutes: Mapped[int] = mapped_column(
        Integer,
        default=0
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(100)
    )

    entity_id: Mapped[str] = mapped_column(
        String(100)
    )

    action: Mapped[str] = mapped_column(
        String(100)
    )

    old_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    new_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# LEGACY MAINTENANCE JOB
# Kept temporarily for existing routes
# ============================================================

class MaintenanceJob(Base):
    __tablename__ = "maintenance_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id")
    )

    department: Mapped[str] = mapped_column(
        String(50)
    )

    section: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING"
    )


# ============================================================
# LEGACY TRAIN MODEL
# Kept temporarily for existing routes
# ============================================================

class Train(Base):
    __tablename__ = "trains"

    id: Mapped[int] = mapped_column(primary_key=True)

    train_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    train_name: Mapped[str] = mapped_column(
        String(100)
    )

    source: Mapped[str] = mapped_column(
        String(100)
    )

    destination: Mapped[str] = mapped_column(
        String(100)
    )

    section: Mapped[str] = mapped_column(
        String(100)
    )

    entry_time: Mapped[str] = mapped_column(
        String(5)
    )

    exit_time: Mapped[str] = mapped_column(
        String(5)
    )