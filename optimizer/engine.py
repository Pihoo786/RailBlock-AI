"""Conflict-aware maintenance block selection for the RailBlock-AI prototype.

The module deliberately uses a transparent rule-based scoring method.  This is
easy to demonstrate, test, and later call from the FastAPI backend.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable
from uuid import uuid4

TIME_FORMAT = "%H:%M"
PRIORITY_RISK = {"LOW": 0.25, "MEDIUM": 0.60, "HIGH": 0.90}

def _minutes(value: str) -> int:
    """Convert a HH:MM time to minutes after midnight."""
    if value == "24:00":
        return 24 * 60

    try:
        parsed = datetime.strptime(value, TIME_FORMAT)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Time must use HH:MM format; got {value!r}.") from exc

    return parsed.hour * 60 + parsed.minute
def _time(value: int) -> str:
    """Convert minutes after midnight to HH:MM, allowing an end time of 24:00."""
    if value == 24 * 60:
        return "24:00"
    return f"{value // 60:02d}:{value % 60:02d}"


def _overlaps(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    """Return True only when two half-open windows overlap."""
    return start_a < end_b and end_a > start_b


def generate_candidate_windows(
    duration_minutes: int,
    available_start: str = "06:00",
    available_end: str = "22:00",
    interval_minutes: int = 30,
) -> list[dict[str, str]]:
    """Generate candidate maintenance windows within the operating day."""
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be greater than zero.")
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be greater than zero.")

    start, end = _minutes(available_start), _minutes(available_end)
    if start >= end:
        raise ValueError("available_start must be before available_end.")

    windows = []
    candidate = start
    while candidate + duration_minutes <= end:
        windows.append({"start_time": _time(candidate), "end_time": _time(candidate + duration_minutes)})
        candidate += interval_minutes
    return windows


def find_conflicting_trains(
    trains: Iterable[dict[str, Any]], section: str, start_time: str, end_time: str
) -> list[dict[str, Any]]:
    """Return timetable entries overlapping the proposed block on its section."""
    block_start, block_end = _minutes(start_time), _minutes(end_time)

    if block_start >= block_end:
        raise ValueError("Block start_time must be before end_time.")

    conflicts = []

    for train in trains:
        if train.get("section") != section:
            continue

        train_start = _minutes(train["entry_time"])
        train_end = _minutes(train["exit_time"])

        # Trains can legitimately cross midnight.
        # Example: 23:58 -> 00:20 means 23:58 -> 24:20.
        if train_end <= train_start:
            train_end += 24 * 60

        if _overlaps(block_start, block_end, train_start, train_end):
            conflicts.append(train)

    return conflicts

def _risk_score(job: dict[str, Any]) -> float:
    raw_score = job.get("risk_score", PRIORITY_RISK.get(job.get("priority", "MEDIUM"), 0.60))
    try:
        score = float(raw_score)
    except (TypeError, ValueError) as exc:
        raise ValueError("risk_score must be a number from 0.0 to 1.0.") from exc
    if not 0.0 <= score <= 1.0:
        raise ValueError("risk_score must be between 0.0 and 1.0.")
    return score


def _impact_level(affected_trains: int) -> str:
    if affected_trains == 0:
        return "LOW"
    if affected_trains <= 2:
        return "MEDIUM"
    return "HIGH"


def _evaluate_window(
    job: dict[str, Any], trains: Iterable[dict[str, Any]], window: dict[str, str]
) -> dict[str, Any]:
    conflicts = find_conflicting_trains(trains, job["section"], window["start_time"], window["end_time"])
    affected_trains = len(conflicts)
    estimated_impact = affected_trains * 5
    # Lower score is better.  A small priority bonus helps urgent work win when
    # two candidates create the same railway disruption.
    score = affected_trains * 10 + estimated_impact - _risk_score(job) * 2
    return {
        **window,
        "affected_trains": affected_trains,
        "affected_train_ids": [train["train_id"] for train in conflicts],
        "estimated_impact_minutes": estimated_impact,
        "impact_level": _impact_level(affected_trains),
        "optimization_score": round(score, 2),
    }


def optimize_maintenance_block(
    maintenance_job: dict[str, Any],
    trains: Iterable[dict[str, Any]],
    *,
    available_start: str = "06:00",
    available_end: str = "22:00",
    interval_minutes: int = 30,
) -> dict[str, Any]:
    """Return the least disruptive recommended block for one maintenance job.

    Required job keys: ``job_id``, ``section`` and ``duration_minutes``.
    ``priority`` and ``risk_score`` are optional while Person 2's module is
    being integrated.
    """
    required = ("job_id", "section", "duration_minutes")
    missing = [key for key in required if key not in maintenance_job]
    if missing:
        raise ValueError(f"Maintenance job is missing required fields: {', '.join(missing)}.")

    duration = maintenance_job["duration_minutes"]
    if not isinstance(duration, int):
        raise ValueError("duration_minutes must be an integer.")
    # Validate early even if the risk bonus does not affect the winning slot.
    risk_score = _risk_score(maintenance_job)
    train_list = list(trains)
    candidates = generate_candidate_windows(duration, available_start, available_end, interval_minutes)
    if not candidates:
        raise ValueError("No candidate window fits within the available operating hours.")

    evaluated = [_evaluate_window(maintenance_job, train_list, window) for window in candidates]
    best = min(evaluated, key=lambda item: (item["optimization_score"], item["start_time"]))
    return {
        "block_id": f"BLK-{uuid4().hex[:8].upper()}",
        "job_id": maintenance_job["job_id"],
        "section": maintenance_job["section"],
        "start_time": best["start_time"],
        "end_time": best["end_time"],
        "departments": [maintenance_job.get("department", "Engineering")],
        "risk_score": risk_score,
        "priority": maintenance_job.get("priority", "MEDIUM"),
        "affected_trains": best["affected_trains"],
        "affected_train_ids": best["affected_train_ids"],
        "estimated_impact_minutes": best["estimated_impact_minutes"],
        "impact_level": best["impact_level"],
        "status": "RECOMMENDED",
        "evaluated_windows": evaluated,
    }


def combine_compatible_jobs(jobs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group same-section jobs into one request when their timing is compatible.

    Jobs with the same section and optional ``requested_date`` are combined.
    The returned duration is the longest required duration, because the work
    can occur inside one shared block; departments are preserved for display.
    """
    groups: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for job in jobs:
        key = (job["section"], job.get("requested_date"))
        groups.setdefault(key, []).append(job)

    combined = []
    for (section, requested_date), group in groups.items():
        lead = max(group, key=lambda job: (_risk_score(job), job["duration_minutes"]))
        item = dict(lead)
        item["job_id"] = "+".join(job["job_id"] for job in group)
        item["section"] = section
        item["duration_minutes"] = max(job["duration_minutes"] for job in group)
        item["departments"] = sorted({job.get("department", "Engineering") for job in group})
        if requested_date:
            item["requested_date"] = requested_date
        combined.append(item)
    return combined
