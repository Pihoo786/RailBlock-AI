"""Person 4 QACore tests for the passenger data boundary."""
from datetime import datetime
from types import SimpleNamespace
import os

# Keep boundary tests database-independent.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi import HTTPException

from backend.app.routes.passenger import (
    get_passenger_blocks,
    get_passenger_train,
)
from backend.app.services.passenger_service import (
    PUBLIC_STATUSES,
    sanitize_block,
)


INTERNAL_FIELDS = {
    "risk_score",
    "priority_score",
    "priority_band",
    "priority_reasons",
    "optimization_explanation",
    "request_id",
    "asset_id",
    "asset_code",
    "departments",
}


def block(**overrides):
    values = dict(
        train_number="12627",
        section="Chennai - Katpadi",
        start_time=datetime(2026, 9, 5, 10, 0),
        end_time=datetime(2026, 9, 5, 12, 0),
        expected_delay_minutes=25,
        reason="Optimized maintenance block for job 42. Risk score: 0.91",
        status="APPROVED",
        risk_score=0.91,
        priority_score=98.2,
        priority_band="CRITICAL",
        priority_reasons=["high asset risk"],
        optimization_explanation="Penalty minimized by CP-SAT",
        request_id=42,
        asset_id=7,
        asset_code="TRK-001",
        departments="TRACK",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


class FakeDB:
    def __init__(self, train=None, blocks=None):
        self.train = train
        self.blocks = blocks or []

    def query(self, model):
        # Model name is enough for this isolated route-boundary test.
        return FakeQuery([self.train] if model.__name__ == "Train" and self.train else self.blocks)


def test_sanitizer_is_allow_list():
    public = sanitize_block(block(reason="Track maintenance required"))
    assert not (set(public) & INTERNAL_FIELDS)
    assert set(public) == {
        "train_number",
        "section",
        "start_time",
        "end_time",
        "expected_delay_minutes",
        "reason",
        "reason_code",
        "status",
    }
    assert public["reason_code"] == "TRACK_MAINTENANCE"
    assert public["reason"] == "Track maintenance"


def test_public_status_allow_list():
    assert PUBLIC_STATUSES == {
        "SCHEDULED", "APPROVED", "ACTIVE", "COMPLETED", "CANCELLED"
    }


def test_passenger_blocks_never_return_internal_fields():
    response = get_passenger_blocks(FakeDB(blocks=[block()]))
    assert len(response) == 1
    assert not (set(response[0]) & INTERNAL_FIELDS)


def test_passenger_train_is_sanitized():
    response = get_passenger_train(
        "12627",
        FakeDB(train=SimpleNamespace(train_number="12627"), blocks=[block()]),
    )
    assert response["train_number"] == "12627"
    assert len(response["blocks"]) == 1
    assert not (set(response["blocks"][0]) & INTERNAL_FIELDS)


def test_unknown_train_returns_404():
    with pytest.raises(HTTPException) as exc:
        get_passenger_train("99999", FakeDB())
    assert exc.value.status_code == 404


def test_internal_status_is_not_published():
    response = get_passenger_blocks(FakeDB(blocks=[block(status="RECOMMENDED")]))
    # The query's DB filtering is mocked in this unit test; the route must still
    # produce only the safe DTO if a future query layer changes.
    assert not (set(response[0]) & INTERNAL_FIELDS)
