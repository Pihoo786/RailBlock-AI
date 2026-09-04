"""
predict.py
----------
The ML -> rest-of-team contract. This is what Dhanvee's backend calls.
Output shape is FROZEN per 06_API_CONTRACT_AND_SHARED_MODELS.md — do not
rename fields without updating that doc and getting the team to confirm.

Run as a standalone API:
    uvicorn predict:app --reload --port 8001

POST /predict
{
  "request_id": "MR-001",
  "asset_age_days": 1500, "days_since_last_maintenance": 40, ... (see FEATURE fields)
}
"""

import pandas as pd
import xgboost as xgb
from fastapi import FastAPI
from pydantic import BaseModel

from explain import RiskExplainer
from preprocessing import (
    load_pipeline, NUMERIC_FEATURES, CATEGORICAL_FEATURES,
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "xgb_v1.json"
PIPELINE_PATH = BASE_DIR / "models" / "preprocessing.joblib"

_model = xgb.XGBClassifier()
_model.load_model(str(MODEL_PATH))
_pipeline = load_pipeline(str(PIPELINE_PATH))
_explainer = RiskExplainer(_model, _pipeline)

MODEL_VERSION = "v1"


def risk_band(prob: float) -> str:
    if prob >= 0.40:
        return "HIGH"
    if prob >= 0.20:
        return "MEDIUM"
    return "LOW"


def predict(request_id: str, features: dict) -> dict:
    """features must contain every key in NUMERIC_FEATURES + CATEGORICAL_FEATURES."""
    features = dict(features)  # don't mutate the caller's dict
    features["effective_age_days"] = features["asset_age_days"] * (features["traffic_density_gmt"] / 20.0) ** 0.6
    row = pd.DataFrame([features])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    X = _pipeline.transform(row)
    prob = float(_model.predict_proba(X)[:, 1][0])
    top_features = _explainer.top_features(X, k=3)
    return {
        "request_id": request_id,
        "failure_probability": round(prob, 4),
        "risk_band": risk_band(prob),
        "model_version": MODEL_VERSION,
        "top_features": top_features,
    }


# ---- FastAPI adapter, this is what Backend actually hits ----
app = FastAPI()


class PredictRequest(BaseModel):
    request_id: str
    asset_age_days: float
    days_since_last_maintenance: float
    days_since_usfd: float | None = None
    days_overdue: float
    historical_defect_count: float
    repeated_defect_count: float
    severity_rank: float
    traffic_density_gmt: float
    track_geometry_index: float | None = None
    duration_minutes: float
    train_count: float
    failure_frequency: float | None = None
    historical_downtime_minutes: float | None = None
    trd_wire_wear_flag: float | None = None
    asset_type: str
    department: str
    criticality_class: str
    block_type: str


@app.post("/predict")
def predict_endpoint(req: PredictRequest):
    payload = req.dict()
    request_id = payload.pop("request_id")
    return predict(request_id, payload)
