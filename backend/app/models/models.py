from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(50), unique=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    section: Mapped[str] = mapped_column(String(100))
    condition_score: Mapped[float] = mapped_column(Float)
    criticality: Mapped[float] = mapped_column(Float)
    overdue_score: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)


class MaintenanceJob(Base):
    __tablename__ = "maintenance_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id")
    )

    department: Mapped[str] = mapped_column(String(50))
    section: Mapped[str] = mapped_column(String(100))

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration_minutes: Mapped[int] = mapped_column(Integer)

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING"
    )


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(
        String(20),
        index=True
    )

    section: Mapped[str] = mapped_column(String(100))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)

    departments: Mapped[str] = mapped_column(String(200))

    affected_trains: Mapped[int] = mapped_column(Integer)

    expected_delay_minutes: Mapped[int] = mapped_column(Integer)

    reason: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(20),
        default="RECOMMENDED"
    )

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


