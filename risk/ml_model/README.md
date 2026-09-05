# ML Risk Model — RailBlock AI (SIH26027)

Predicts `failure_probability` = P(asset fails within 30 days of a maintenance
request being raised), using XGBoost, trained on Rishita's real generated dataset
(`assets.csv`, `defects.csv`, `block_requests.csv`, `historical_outcomes.csv`,
`sections.csv`, `signal_failures.csv`).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install xgboost scikit-learn shap pandas numpy joblib fastapi uvicorn matplotlib
```

Put the 6 raw CSVs in `data/` (already done if you're reading this from the
generated project).

## Run everything, in order

```bash
python src/build_dataset.py   # raw CSVs -> data/training_table.csv (one row per request)
python src/train.py           # trains XGBoost -> models/xgb_v1.json, models/preprocessing.joblib
python src/evaluate.py        # PR-AUC, Precision@K, calibration, confusion matrix -> reports/
python -c "from src.predict import predict; print('ready')"   # sanity check imports
```

## Serve predictions (what Backend calls)

```bash
cd src && uvicorn predict:app --reload --port 8001
```
`POST /predict` with the feature fields listed in `predict.py`'s `PredictRequest`
model. Returns the frozen contract shape:
```json
{
  "request_id": "MR-001",
  "failure_probability": 0.87,
  "risk_band": "HIGH",
  "model_version": "v1",
  "top_features": [{"feature": "repeated_defect_count", "impact": 0.24}]
}
```

## Retrain on new outcomes

```bash
python src/retrain.py --new_outcomes data/new_outcomes.csv
```
Only promotes the new model if its PR-AUC on the same held-out test split is
≥ the current model's. Otherwise the live model is untouched.

## What's in `data/training_table.csv`

One row = one maintenance request, as of the moment it was raised. Every
feature is computed using only information available at that timestamp —
no defect, failure, or downtime that happened *after* the request is allowed
into a feature. The label (`failed_within_30_days`) comes from
`historical_outcomes.csv`, observed exactly 30 days later.

**Feature schema** (also see `src/preprocessing.py` — this is the frozen list,
share it with Backend and AI/Optimization before it changes):

| Column | Group | Notes |
|---|---|---|
| asset_age_days | common | snapshot − install_date |
| days_since_last_maintenance | common | snapshot − last_maintenance_date |
| days_since_usfd | common | Engineering only, NaN elsewhere |
| days_overdue | common | **assumption**: `max(0, days_since_last_maintenance − standard_interval)`; interval is a placeholder per department in `build_dataset.py` — replace with the real SLA if the team has one |
| historical_defect_count | common | defects on this asset before the snapshot |
| repeated_defect_count | common | prior defects of the *same category* as the triggering one |
| severity_rank | common | ordinal encoding of the triggering defect's severity (routine=0 … urgent=4) |
| asset_type, department, criticality_class, block_type | common | categorical |
| traffic_density_gmt, track_geometry_index | Engineering | track_geometry_index NaN outside Engineering |
| duration_minutes, train_count | common | requested block duration; section train volume |
| failure_frequency, historical_downtime_minutes | S&T | count/sum of signal failures before snapshot, NaN outside S&T |
| trd_wire_wear_flag | TRD | 1 if triggering defect is a wire/OHE-wear category, NaN outside TRD |

## Known limitations to say out loud to judges

- **Positive rate is ~2.9%** (117 failures out of 3999 requests) — this is by
  design (rare-event realism), but it means PR-AUC and Precision@K are the
  metrics that matter, not accuracy.
- **`days_overdue`** is derived from an assumed maintenance interval, not a
  real SLA field — flagged clearly above, swap it out if a real one turns up.
- **S&T and TRD department-specific features are sparser** than Engineering's
  (no direct "wire wear" or "OHE condition index" sensor data exists in the
  synthetic set — `trd_wire_wear_flag` is a proxy built from defect category).

## Files

```
data/                  raw CSVs + built training_table.csv
src/build_dataset.py   raw CSVs -> training_table.csv (feature engineering, no leakage)
src/preprocessing.py   shared preprocessing pipeline (train + predict both import this)
src/train.py           chronological split + XGBoost training
src/evaluate.py        PR-AUC / Precision@K / calibration / confusion matrix
src/explain.py         SHAP TreeExplainer wrapper
src/predict.py         prediction function + FastAPI adapter (the API contract)
src/retrain.py         retrain-and-promote-if-better
models/                xgb_v1.json, preprocessing.joblib (created by train.py)
reports/               evaluation_report.md/json, calibration_curve.png
```
