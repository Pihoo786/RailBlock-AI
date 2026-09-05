"""Passenger-facing data boundary.

This module is deliberately allow-list based: only fields required by the
public portal are copied from internal Block records. Internal risk scores,
priority/penalty fields, department data, request IDs, and optimization
explanations never cross the passenger API boundary.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

PUBLIC_STATUSES = {"SCHEDULED", "APPROVED", "ACTIVE", "COMPLETED", "CANCELLED"}

# Stable public reason codes. Internal optimization wording is never exposed.
REASON_CODES = {
    "track": ("TRACK_MAINTENANCE", "Track maintenance"),
    "ohe": ("OHE_INSPECTION", "Overhead equipment inspection"),
    "catenary": ("OHE_INSPECTION", "Overhead equipment inspection"),
    "signal": ("SIGNAL_MAINTENANCE", "Signalling maintenance"),
    "s&t": ("SIGNAL_MAINTENANCE", "Signalling maintenance"),
    "electrical": ("ELECTRICAL_WORK", "Electrical maintenance"),
    "bridge": ("STRUCTURE_MAINTENANCE", "Structure maintenance"),
}


def public_reason(reason: str | None) -> tuple[str, str]:
    """Return a stable public reason code + passenger-safe label."""
    text = (reason or "").lower()
    for keyword, value in REASON_CODES.items():
        if keyword in text:
            return value
    return "OTHER_MAINTENANCE", "Railway maintenance"


def sanitize_block(block: Any) -> dict[str, Any]:
    """Convert an ORM block into an explicit public DTO.

    Do not replace this allow-list with ``model_dump()`` or ``__dict__``:
    doing so risks leaking newly added internal columns in future.
    """
    status = str(getattr(block, "status", "SCHEDULED")).upper()
    if status not in PUBLIC_STATUSES:
        status = "SCHEDULED"

    code, label = public_reason(getattr(block, "reason", None))

    return {
        "train_number": getattr(block, "train_number", None),
        "section": getattr(block, "section", None),
        "start_time": getattr(block, "start_time", None),
        "end_time": getattr(block, "end_time", None),
        "expected_delay_minutes": int(getattr(block, "expected_delay_minutes", 0) or 0),
        "reason": label,
        "reason_code": code,
        "status": status,
    }


def is_public_status(status: str | None) -> bool:
    return str(status or "").upper() in PUBLIC_STATUSES
