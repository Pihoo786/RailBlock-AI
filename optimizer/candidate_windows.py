"""Candidate maintenance-window generation and train conflict detection."""

from __future__ import annotations

from typing import Any, Iterable

from .compatibility import are_compatible, normalize_block_type
from .engine import _minutes, _time, find_conflicting_trains, generate_candidate_windows


def _windows_overlap(first: dict[str, Any], second: dict[str, Any]) -> bool:
    return _minutes(first["start_time"]) < _minutes(second["end_time"]) and _minutes(first["end_time"]) > _minutes(second["start_time"])


def candidate_id(request_id: str, start_time: str, end_time: str) -> str:
    return f"{request_id}@{start_time}-{end_time}"


def generate_feasible_candidates(
    request: dict[str, Any],
    trains: Iterable[dict[str, Any]],
    *,
    existing_blocks: Iterable[dict[str, Any]] = (),
    rejected_candidate_ids: Iterable[str] = (),
    available_start: str = "06:00",
    available_end: str = "22:00",
    interval_minutes: int = 30,
) -> list[dict[str, Any]]:
    """Return windows that fit duration and have no hard traffic/block conflict."""
    required = ("request_id", "section", "duration_minutes")
    missing = [field for field in required if field not in request]
    if missing:
        raise ValueError(f"Request is missing: {', '.join(missing)}")
    request_type = normalize_block_type(request.get("block_type"))
    rejected = set(rejected_candidate_ids) | set(request.get("rejected_candidate_ids", []))
    all_windows = generate_candidate_windows(request["duration_minutes"], available_start, available_end, interval_minutes)
    feasible: list[dict[str, Any]] = []

    for window in all_windows:
        key = candidate_id(request["request_id"], window["start_time"], window["end_time"])
        if key in rejected:
            continue
        conflicts = find_conflicting_trains(trains, request["section"], window["start_time"], window["end_time"])
        # Train occupancy is a hard constraint in the MVP, not a soft penalty.
        if conflicts:
            continue
        block_conflict = any(
            block.get("section") == request["section"]
            and _windows_overlap(window, block)
            and not are_compatible(request_type, block.get("block_type"))
            for block in existing_blocks
        )
        if block_conflict:
            continue
        feasible.append(
            {
                "candidate_id": key,
                "request_id": request["request_id"],
                "section": request["section"],
                "start_time": window["start_time"],
                "end_time": window["end_time"],
                "block_type": request_type,
                "departments": [request.get("department", "Engineering")],
                "affected_trains": 0,
                "affected_train_ids": [],
                "affected_train_minutes": 0,
            }
        )
    return feasible


def explain_rejected_windows(request: dict[str, Any], trains: Iterable[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
    """Return every window with conflict details for explainability/debugging."""
    result = []
    for window in generate_candidate_windows(request["duration_minutes"], kwargs.get("available_start", "06:00"), kwargs.get("available_end", "22:00"), kwargs.get("interval_minutes", 30)):
        conflicts = find_conflicting_trains(trains, request["section"], window["start_time"], window["end_time"])
        result.append({
            **window,
            "candidate_id": candidate_id(request["request_id"], window["start_time"], window["end_time"]),
            "conflicting_trains": [train["train_id"] for train in conflicts],
            "feasible_for_traffic": not conflicts,
        })
    return result
