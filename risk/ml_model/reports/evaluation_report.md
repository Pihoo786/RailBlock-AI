# Evaluation Report

Test set: 600 rows (newest 15% chronologically), positive rate 0.0283

| Metric | Value |
|---|---|
| PR-AUC | 0.0577 |
| Precision@20 | 0.0500 |
| Precision @ threshold 0.5 | 0.1111 |
| Recall @ threshold 0.5 | 0.0588 |

Confusion matrix @ threshold 0.5:

|  | Predicted 0 | Predicted 1 |
|---|---|---|
| Actual 0 | 575 | 8 |
| Actual 1 | 16 | 1 |

Calibration curve saved to `reports/calibration_curve.png`.

Accuracy is not reported as a headline number: with a ~3% positive
rate, a model that always predicts "no failure" scores ~97% accuracy
while being useless. PR-AUC and Precision@K are the numbers that
actually reflect whether this model finds the assets that fail.
