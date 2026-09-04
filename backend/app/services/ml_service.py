import os

import httpx


ML_SERVICE_URL = os.getenv(
    "ML_SERVICE_URL",
    "http://127.0.0.1:8001",
)


def predict_risk(features: dict) -> dict:
    """Call the standalone ML risk service."""

    response = httpx.post(
        f"{ML_SERVICE_URL}/predict",
        json=features,
        timeout=30.0,
    )

    response.raise_for_status()

    return response.json()