"""Batch maintenance planning with Google OR-Tools CP-SAT."""

from __future__ import annotations

from typing import Any, Iterable

from ortools.sat.python import cp_model

from .candidate_windows import generate_feasible_candidates
from .compatibility import are_compatible
from .engine import _minutes
from .priority_engine import priority_decision


PRIORITY_WEIGHT = {"LOW": 1, "MEDIUM": 3, "HIGH": 8, "CRITICAL": 15}


def _overlap(first: dict[str, Any], second: dict[str, Any]) -> bool:
    return _minutes(first["start_time"]) < _minutes(second["end_time"]) and _minutes(first["end_time"]) > _minutes(second["start_time"])


def optimize_plan(
    requests: Iterable[dict[str, Any]],
    ml_outputs: Iterable[dict[str, Any]],
    trains: Iterable[dict[str, Any]],
    *,
    existing_blocks: Iterable[dict[str, Any]] = (),
    rejected_candidates: dict[str, list[str]] | None = None,
    available_start: str = "06:00",
    available_end: str = "22:00",
    interval_minutes: int = 30,
) -> dict[str, Any]:
    """Create a feasible weekly/monthly plan for pending maintenance requests.

    A request receives at most one candidate.  Overlapping incompatible blocks
    on the same section cannot both be selected.  High priority work receives a
    much larger penalty when unscheduled.
    """
    request_list = list(requests)
    train_list = list(trains)
    ml_by_request = {item["request_id"]: item for item in ml_outputs}
    rejected_candidates = rejected_candidates or {}

    priorities = {
        request["request_id"]: priority_decision(request, ml_by_request.get(request["request_id"], {}))
        for request in request_list
    }
    candidates_by_request = {
        request["request_id"]: generate_feasible_candidates(
            request,
            train_list,
            existing_blocks=existing_blocks,
            rejected_candidate_ids=rejected_candidates.get(request["request_id"], []),
            available_start=available_start,
            available_end=available_end,
            interval_minutes=interval_minutes,
        )
        for request in request_list
    }

    model = cp_model.CpModel()
    variables: dict[str, Any] = {}
    candidate_lookup: dict[str, dict[str, Any]] = {}
    for candidates in candidates_by_request.values():
        for candidate in candidates:
            candidate_lookup[candidate["candidate_id"]] = candidate
            variables[candidate["candidate_id"]] = model.NewBoolVar(candidate["candidate_id"])

    # One chosen candidate at most per maintenance request.
    for request in request_list:
        ids = [candidate["candidate_id"] for candidate in candidates_by_request[request["request_id"]]]
        if ids:
            model.Add(sum(variables[candidate_id] for candidate_id in ids) <= 1)

    ids = list(candidate_lookup)
    for index, first_id in enumerate(ids):
        first = candidate_lookup[first_id]
        for second_id in ids[index + 1 :]:
            second = candidate_lookup[second_id]
            if first["request_id"] == second["request_id"]:
                continue
            if first["section"] == second["section"] and _overlap(first, second) and not are_compatible(first["block_type"], second["block_type"]):
                model.Add(variables[first_id] + variables[second_id] <= 1)

    # CP-SAT minimizes unscheduled high-priority work first, then operational cost.
    objective_terms = []
    for request in request_list:
        request_id = request["request_id"]
        weight = PRIORITY_WEIGHT[priorities[request_id]["priority_band"]]
        chosen = [variables[item["candidate_id"]] for item in candidates_by_request[request_id]]
        if chosen:
            objective_terms.append((1 - sum(chosen)) * weight * 1000)
    for candidate_id, candidate in candidate_lookup.items():
        objective_terms.append(variables[candidate_id] * candidate["affected_train_minutes"])
        # Stable tie-breaker: prefer an earlier equally safe block.
        objective_terms.append(variables[candidate_id] * (_minutes(candidate["start_time"]) // 30))
    model.Minimize(sum(objective_terms) if objective_terms else 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("CP-SAT could not find a feasible maintenance plan.")

    planned, unscheduled = [], []
    for request in request_list:
        request_id = request["request_id"]
        selected = next((candidate for candidate in candidates_by_request[request_id] if solver.Value(variables[candidate["candidate_id"]])), None)
        if selected is None:
            reason = "No traffic-safe candidate window is available."
            if candidates_by_request[request_id]:
                reason = "All traffic-safe candidates overlap with a higher-value incompatible block."
            unscheduled.append({"request_id": request_id, "priority": priorities[request_id], "reason": reason})
            continue
        planned.append({
            **selected,
            "priority": priorities[request_id],
            "expected_disruption_minutes": selected["affected_train_minutes"],
            "explanation": "Selected by CP-SAT: traffic-safe and compatible with the optimized plan.",
            "status": "RECOMMENDED",
        })
    planned.sort(key=lambda item: (item["section"], item["start_time"]))
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for item in planned:
        grouped.setdefault((item["section"], item["start_time"], item["end_time"], item["block_type"]), []).append(item)
    for group in grouped.values():
        if len(group) <= 1:
            continue
        request_ids = [item["request_id"] for item in group]
        departments = sorted({department for item in group for department in item["departments"]})
        for item in group:
            item["grouped_request_ids"] = request_ids
            item["departments"] = departments
            item["explanation"] = "Selected by CP-SAT as one compatible multi-department maintenance block."
    return {
        "solver": "Google OR-Tools CP-SAT",
        "plan": planned,
        "unscheduled_items": unscheduled,
        "priority_decisions": priorities,
    }


def reoptimize_after_rejection(
    rejected_block: dict[str, Any], requests: Iterable[dict[str, Any]], ml_outputs: Iterable[dict[str, Any]], trains: Iterable[dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    """Exclude a rejected candidate and return the next best feasible plan."""
    request_id = rejected_block["request_id"]
    rejected = dict(kwargs.pop("rejected_candidates", {}))
    rejected[request_id] = [*rejected.get(request_id, []), rejected_block["candidate_id"]]
    return optimize_plan(requests, ml_outputs, trains, rejected_candidates=rejected, **kwargs)


def recommend_single(
    request: dict[str, Any], ml_output: dict[str, Any], trains: Iterable[dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    """Return one recommendation plus feasible alternatives for an API caller."""
    plan = optimize_plan([request], [ml_output], trains, **kwargs)
    selected = plan["plan"][0] if plan["plan"] else None
    candidates = generate_feasible_candidates(
        request,
        trains,
        existing_blocks=kwargs.get("existing_blocks", ()),
        rejected_candidate_ids=kwargs.get("rejected_candidates", {}).get(request["request_id"], []),
        available_start=kwargs.get("available_start", "06:00"),
        available_end=kwargs.get("available_end", "22:00"),
        interval_minutes=kwargs.get("interval_minutes", 30),
    )
    alternatives = [candidate for candidate in candidates if not selected or candidate["candidate_id"] != selected["candidate_id"]][:3]
    return {
        "recommended_block": selected,
        "alternatives": alternatives,
        "unscheduled_items": plan["unscheduled_items"],
        "priority": plan["priority_decisions"][request["request_id"]],
    }
