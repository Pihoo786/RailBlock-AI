"""Explicit maintenance-block compatibility rules.

Compatibility is deliberately restrictive.  New pairings must be reviewed and
added here; the planner never assumes departments can share a block.
"""

from __future__ import annotations

from typing import Iterable


BLOCK_TYPES = {"TRAFFIC", "POWER", "DISCONNECTION"}
COMPATIBILITY: dict[frozenset[str], bool] = {
    frozenset({"TRAFFIC"}): True,
    frozenset({"POWER"}): True,
    frozenset({"DISCONNECTION"}): True,
    frozenset({"TRAFFIC", "POWER"}): False,
    frozenset({"TRAFFIC", "DISCONNECTION"}): False,
    frozenset({"POWER", "DISCONNECTION"}): False,
}


def normalize_block_type(value: str | None) -> str:
    block_type = (value or "TRAFFIC").upper().replace(" ", "_")
    if block_type not in BLOCK_TYPES:
        raise ValueError(f"Unsupported block type {value!r}. Use one of: {', '.join(sorted(BLOCK_TYPES))}.")
    return block_type


def are_compatible(first: str | None, second: str | None) -> bool:
    """Return the reviewed compatibility decision for two block categories."""
    return COMPATIBILITY[frozenset({normalize_block_type(first), normalize_block_type(second)})]


def compatible_departments(requests: Iterable[dict]) -> bool:
    """Only group requests when every proposed block type is explicitly compatible."""
    types = [normalize_block_type(request.get("block_type")) for request in requests]
    return all(are_compatible(first, second) for index, first in enumerate(types) for second in types[index + 1 :])
