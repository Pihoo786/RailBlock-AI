"""
evaluate.py
-----------
Evaluates the trained model on the chronological TEST split.
Accuracy alone is not reported as a headline metric on purpose --
with a ~3% positive rate, "always predict 0" gets ~97% accuracy and
is useless. We report PR-AUC, Precision@K, calibration, and a
confusion matrix at a chosen operating threshold instead.

Run:
    python src/evaluate.py
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xgboost as xgb
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score, confusion_matrix, precision_score, recall_score,
)

from preprocessing import (
    load_training_table, load_pipeline, NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET,
)
from train import chronological_split

MODEL_PATH = "models/xgb_v1.json"
THRESHOLD = 0.5  # tune this after looking at the PR curve / your ops constraints
K = 20           # Precision@K: of the K riskiest assets this model flags, how many actually fail?


def main():
    df = load_training_table()
    _, _, test = chronological_split(df)
    X_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    pipeline = load_pipeline()
    X_test = pipeline.transform(test[X_cols])
    y_test = test[TARGET].values

    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    probs = model.predict_proba(X_test)[:, 1]

    from sklearn.metrics import precision_recall_curve

    precisions, recalls, thresholds = precision_recall_curve(y_test, probs)
    for p, r, t in zip(precisions, recalls, thresholds):
        if r >= 0.3:  # find a threshold that catches ~30%+ of real failures
            print(f"threshold={t:.4f}  precision={p:.4f}  recall={r:.4f}")
            break

    print("prob stats:", probs.min(), probs.max(), probs.mean())
    for target_recall in [0.2, 0.3, 0.4, 0.5]:
        for p, r, t in zip(precisions, recalls, thresholds):
            if r <= target_recall:
                print(f"target_recall~{target_recall}: threshold={t:.4f} precision={p:.4f} recall={r:.4f}")
                break

    # --- PR-AUC ---
    pr_auc = average_precision_score(y_test, probs)

    # --- Precision@K ---
    top_k_idx = np.argsort(-probs)[:K]
    precision_at_k = y_test[top_k_idx].mean() if len(top_k_idx) else float("nan")

    # --- confusion matrix + precision/recall at chosen threshold ---
    preds = (probs >= THRESHOLD).astype(int)
    cm = confusion_matrix(y_test, preds)
    precision = precision_score(y_test, preds, zero_division=0)
    recall = recall_score(y_test, preds, zero_division=0)

    # --- calibration plot ---
    frac_pos, mean_pred = calibration_curve(y_test, probs, n_bins=10, strategy="quantile")
    plt.figure()
    plt.plot(mean_pred, frac_pos, marker="o", label="model")
    plt.plot([0, 1], [0, 1], linestyle="--", label="perfectly calibrated")
    plt.xlabel("mean predicted probability")
    plt.ylabel("observed failure rate")
    plt.title("Calibration curve")
    plt.legend()
    plt.savefig("reports/calibration_curve.png", bbox_inches="tight")

    report = {
        "test_rows": len(test),
        "test_positive_rate": float(y_test.mean()),
        "pr_auc": float(pr_auc),
        f"precision_at_{K}": float(precision_at_k),
        "threshold": THRESHOLD,
        "precision_at_threshold": float(precision),
        "recall_at_threshold": float(recall),
        "confusion_matrix": {
            "tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]), "tp": int(cm[1, 1]),
        },
    }

    with open("reports/evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    md = f"""# Evaluation Report

Test set: {report['test_rows']} rows (newest 15% chronologically), positive rate {report['test_positive_rate']:.4f}

| Metric | Value |
|---|---|
| PR-AUC | {report['pr_auc']:.4f} |
| Precision@{K} | {report[f'precision_at_{K}']:.4f} |
| Precision @ threshold {THRESHOLD} | {report['precision_at_threshold']:.4f} |
| Recall @ threshold {THRESHOLD} | {report['recall_at_threshold']:.4f} |

Confusion matrix @ threshold {THRESHOLD}:

|  | Predicted 0 | Predicted 1 |
|---|---|---|
| Actual 0 | {cm[0,0]} | {cm[0,1]} |
| Actual 1 | {cm[1,0]} | {cm[1,1]} |

Calibration curve saved to `reports/calibration_curve.png`.

Accuracy is not reported as a headline number: with a ~3% positive
rate, a model that always predicts "no failure" scores ~97% accuracy
while being useless. PR-AUC and Precision@K are the numbers that
actually reflect whether this model finds the assets that fail.
"""
    with open("reports/evaluation_report.md", "w") as f:
        f.write(md)

    print(md)


if __name__ == "__main__":
    main()
