"""Run a complete Person 1 demo using the supplied synthetic data."""

import json
from pathlib import Path

from optimizer.engine import optimize_maintenance_block


ROOT = Path(__file__).resolve().parents[1]


def load_json(name: str):
    return json.loads((ROOT / "data" / "synthetic" / name).read_text())


if __name__ == "__main__":
    trains = load_json("trains.json")
    job = load_json("maintenance_jobs.json")[0]
    result = optimize_maintenance_block(job, trains)
    print(json.dumps(result, indent=2))
