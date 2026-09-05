"""
explain.py
----------
SHAP explainer for the trained model. Loaded once and reused by predict.py
(TreeExplainer construction is not free, don't rebuild it per-request).
"""

import shap

from preprocessing import get_feature_names


class RiskExplainer:
    def __init__(self, model, pipeline):
        self.explainer = shap.TreeExplainer(model)
        self.feature_names = get_feature_names(pipeline)

    def top_features(self, X_row, k=3):
        """X_row: a single-row transformed feature matrix (already preprocessed)."""
        shap_values = self.explainer(X_row)
        row = shap_values[0]
        order = sorted(range(len(row.values)), key=lambda i: -abs(row.values[i]))[:k]
        return [
            {"feature": self.feature_names[i], "impact": round(float(row.values[i]), 4)}
            for i in order
        ]
