# Person 1: AI and Optimization

This module converts ML risk predictions and railway operating constraints into
feasible maintenance-block plans. It implements the Person 1 work document.

## What is included

- `priority_engine.py` - explainable decision logic over ML risk output
- `candidate_windows.py` - traffic-safe candidate generation and conflict rule
- `compatibility.py` - explicit Traffic/Power/Disconnection compatibility rules
- `cp_sat_optimizer.py` - Google OR-Tools CP-SAT single, batch, and re-planning
- `engine.py` - backwards-compatible simple optimizer used by the current API
- `sample_input.json` and `sample_output.json` - integration examples

## Install and test

```bash
python3 -m pip install -r backend/requirements.txt
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Main API

```python
from optimizer import optimize_plan, recommend_single

weekly_plan = optimize_plan(requests, ml_outputs, trains)
single_result = recommend_single(request, ml_output, trains)
```

`optimize_plan` accepts 10 or more pending requests and returns a plan,
priority decisions, and clear reasons for unscheduled work.

## Decision rules

Priority is explainable decision logic, not ML. It combines predicted failure
probability, asset criticality, operational impact, days overdue, and severity.
Candidate windows use the mandatory conflict rule:

```text
train.entry_time < block.end_time AND train.exit_time > block.start_time
```

Train occupancy is a hard constraint in this MVP. A window with a train
conflict is not proposed. CP-SAT also prevents overlapping incompatible blocks
on the same section and strongly penalizes unscheduled critical work.

Only reviewed compatibility pairs can share a block. The default policy does
not combine Traffic, Power, or Disconnection blocks with a different type.

## Re-optimization

Pass a rejected recommendation to `reoptimize_after_rejection`. Its candidate
ID is excluded and CP-SAT returns the next best feasible block.

## Person 1 unified deliverable

`optimization_engine.py` is the integration facade for the complete Person 1
module. It adds:

- Multi-asset risk scoring for Track, Catenary/TRD, Locomotive, Coach and Wagon assets.
- Age, condition, maintenance-cycle overdue, criticality, safety and history factors.
- Co-planning helpers for compatible same-section maintenance work.
- Rolling-stock clustering against recommended block windows and nearby sections/sheds.
- JSON-safe output for direct FastAPI integration.
- The existing OR-Tools CP-SAT planner remains the authoritative timetable and block-conflict solver.

Main call:

```python
from optimizer.optimization_engine import optimize_multi_asset_plan
result = optimize_multi_asset_plan(requests, trains, assets=assets, rolling_stock=rolling_stock, ml_outputs=ml_outputs)
```
