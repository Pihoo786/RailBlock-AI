"""
retrain.py
----------
Called when Backend has newly logged, validated outcomes.
Only overwrites the live model if the candidate beats the current
model's PR-AUC on the SAME held-out test set (no cheating by testing
on easier data).

Run:
    python src/retrain.py --new_outcomes data/new_outcomes.csv
"""

import argparse
import shutil

import pandas as pd
import xgboost as xgb
from sklearn.metrics import average_precision_score

from preprocessing import (
    build_pipeline, load_training_table, load_pipeline, save_pipeline,
    NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET,
)
from train import chronological_split, MODEL_PATH, PIPELINE_PATH

CANDIDATE_MODEL_PATH = "models/xgb_candidate.json"


def current_model_pr_auc(test, pipeline):
    X_test = pipeline.transform(test[NUMERIC_FEATURES + CATEGORICAL_FEATURES])
    y_test = test[TARGET]
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    probs = model.predict_proba(X_test)[:, 1]
    return average_precision_score(y_test, probs)


def main(new_outcomes_path: str | None):
    df = load_training_table()

    if new_outcomes_path:
        new_rows = pd.read_csv(new_outcomes_path, parse_dates=["requested_at"])
        df = pd.concat([df, new_rows], ignore_index=True).drop_duplicates("request_id")
        print(f"Appended {len(new_rows)} new validated rows -> {len(df)} total")

    train, val, test = chronological_split(df)
    X_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    candidate_pipeline = build_pipeline()
    X_train = candidate_pipeline.fit_transform(train[X_cols])
    X_val = candidate_pipeline.transform(val[X_cols])
    y_train, y_val = train[TARGET], val[TARGET]

    scale_pos_weight = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    candidate = xgb.XGBClassifier(
    n_estimators=300, max_depth=5, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight, eval_metric="aucpr", random_state=42,
    )
    candidate.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    candidate.save_model(CANDIDATE_MODEL_PATH)

    # compare on the SAME test split, using the CURRENT (already-fit) pipeline
    # so the comparison is apples-to-apples
    old_pipeline = load_pipeline(PIPELINE_PATH)
    old_pr_auc = current_model_pr_auc(test, old_pipeline)

    X_test_candidate = candidate_pipeline.transform(test[X_cols])
    candidate_pr_auc = average_precision_score(test[TARGET], candidate.predict_proba(X_test_candidate)[:, 1])

    print(f"current model PR-AUC:   {old_pr_auc:.4f}")
    print(f"candidate model PR-AUC: {candidate_pr_auc:.4f}")

    if candidate_pr_auc >= old_pr_auc:
        shutil.copy(CANDIDATE_MODEL_PATH, MODEL_PATH)
        save_pipeline(candidate_pipeline, PIPELINE_PATH)
        df.to_csv("data/training_table.csv", index=False)
        print("Candidate PROMOTED to live model.")
    else:
        print("Candidate did NOT beat current model. Live model unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--new_outcomes", default=None, help="CSV of newly validated outcome rows, same schema as training_table.csv")
    args = parser.parse_args()
    main(args.new_outcomes)
