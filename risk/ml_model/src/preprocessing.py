"""
preprocessing.py
-----------------
ONE preprocessing pipeline, used by both train.py and predict.py.
This is the #1 hackathon bug to avoid: training-time and prediction-time
preprocessing silently drifting apart. Import from here, don't rewrite it.
"""
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
DATA_DIR = SRC_DIR / "data"
MODELS_DIR = SRC_DIR.parent / "models"
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

NUMERIC_FEATURES = [
    "asset_age_days", "days_since_last_maintenance", "days_since_usfd",
    "days_overdue", "historical_defect_count", "repeated_defect_count",
    "severity_rank", "traffic_density_gmt", "track_geometry_index",
    "duration_minutes", "train_count", "failure_frequency",
    "historical_downtime_minutes", "trd_wire_wear_flag","effective_age_days"
]

CATEGORICAL_FEATURES = ["asset_type", "department", "criticality_class", "block_type"]

TARGET = "failed_within_30_days"

ID_COLS = ["request_id", "asset_id", "requested_at"]


def build_pipeline():
    numeric = Pipeline([("impute", SimpleImputer(strategy="median"))])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="UNKNOWN")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", numeric, NUMERIC_FEATURES),
        ("cat", categorical, CATEGORICAL_FEATURES),
    ])

def load_training_table(path=None):
    if path is None:
        path = DATA_DIR / "training_table.csv"

    df = pd.read_csv(path, parse_dates=["requested_at"])
    return df

def get_feature_names(fitted_pipeline):
    """Flat list of output column names after the ColumnTransformer, for SHAP labeling."""
    cat_encoder = fitted_pipeline.named_transformers_["cat"].named_steps["onehot"]
    cat_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    return NUMERIC_FEATURES + cat_names
def save_pipeline(pipeline, path=None):
    if path is None:
        path = MODELS_DIR / "preprocessing.joblib"

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)

def load_pipeline(path=None):
    if path is None:
        path = MODELS_DIR / "preprocessing.joblib"

    return joblib.load(path)