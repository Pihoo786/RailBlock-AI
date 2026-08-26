# Person 1: Data and Optimization

This folder contains the rule-based maintenance block optimizer.  It is the
prototype's decision engine: it tests possible maintenance windows, detects
overlapping trains, estimates disruption, and recommends the least disruptive
block.

## Run the demo

From the project root, run:

```bash
python3 -m optimizer.demo
```

The demo reads `data/synthetic/trains.json` and
`data/synthetic/maintenance_jobs.json`, then prints a recommended block as
JSON.  No external packages are required.

## Run the tests

```bash
python3 -m unittest tests/test_optimizer.py
```

## Main function

```python
from optimizer.engine import optimize_maintenance_block

result = optimize_maintenance_block(maintenance_job, trains)
```

`maintenance_job` requires `job_id`, `section`, and `duration_minutes`.
`priority` and `risk_score` are optional until the Risk module is connected.

## API-ready response

The result follows the shared schema and contains `block_id`, timing,
`affected_trains`, `affected_train_ids`, `estimated_impact_minutes`,
`impact_level`, and `status`.  It also includes `evaluated_windows`, which the
dashboard can use to show why one block was selected.

## Optimization rules

- Candidate windows run every 30 minutes between 06:00 and 22:00 by default.
- A train conflicts when it overlaps the proposed block on the same section.
- Each conflicting train adds 5 estimated impact minutes.
- The lowest disruption score wins. Risk provides a small tie-break priority.
- `combine_compatible_jobs` groups same-section work into one shared block.
