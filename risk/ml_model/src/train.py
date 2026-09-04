"""
train.py
--------
Chronological split -> preprocess -> train XGBoost with scale_pos_weight
for the rare-failure class imbalance -> save model + pipeline.

Run:
    python src/train.py
Requires:
    pip install xgboost scikit-learn pandas joblib
"""

import joblib
import numpy as np
import xgboost as xgb

from preprocessing import (
    build_pipeline, load_training_table, save_pipeline,
    NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET,
)

MODEL_PATH = "models/xgb_v1.json"
PIPELINE_PATH = "models/preprocessing.joblib"


def chronological_split(df):
    df = df.sort_values("requested_at").reset_index(drop=True)
    n = len(df)
    train = df.iloc[: int(n * 0.70)]
    val = df.iloc[int(n * 0.70): int(n * 0.85)]
    test = df.iloc[int(n * 0.85):]
    print(f"train={len(train)}  val={len(val)}  test={len(test)}")
    print(f"train positive rate={train[TARGET].mean():.4f}  "
          f"val positive rate={val[TARGET].mean():.4f}  "
          f"test positive rate={test[TARGET].mean():.4f}")
    return train, val, test


def main():
    df = load_training_table()
    train, val, test = chronological_split(df)

    X_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    pipeline = build_pipeline()
    X_train = pipeline.fit_transform(train[X_cols])
    X_val = pipeline.transform(val[X_cols])
    X_test = pipeline.transform(test[X_cols])

    y_train, y_val, y_test = train[TARGET], val[TARGET], test[TARGET]

    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos_weight = neg / max(pos, 1)
    print(f"scale_pos_weight = {scale_pos_weight:.2f}  (neg={neg}, pos={pos})")

    model = xgb.XGBClassifier(
    n_estimators=500, max_depth=3, learning_rate=0.03,
    subsample=0.8, colsample_bytree=0.6,
    min_child_weight=5, reg_lambda=2.0,
    scale_pos_weight=scale_pos_weight, eval_metric="aucpr", random_state=42,
)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    model.save_model(MODEL_PATH)
    save_pipeline(pipeline, PIPELINE_PATH)
    # also persist the raw val/test splits so evaluate.py doesn't need to re-split
    joblib.dump({"test_idx": test.index.tolist()}, "models/split_indices.joblib")
    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved pipeline -> {PIPELINE_PATH}")


if __name__ == "__main__":
    main()
