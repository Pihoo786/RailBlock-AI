"""
build_dataset.py
-----------------
Turns the raw RailBlock AI CSVs into ONE training-ready table:
    one row = one maintenance request (the moment it was raised)
    label   = failed_within_30_days (from historical_outcomes.csv)

Every feature is computed using ONLY information that existed at
`requested_at` — nothing from after that timestamp is allowed in.

Run:
    python src/build_dataset.py
Output:
    data/training_table.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parents[2]

DATA_DIR = PROJECT_ROOT / "dataset" / "extracted" / "railblock_dataset"
OUT_PATH = SRC_DIR / "data" / "training_table.csv"

# Assumed standard maintenance interval per department, in days.
# Used only to derive `days_overdue` from `days_since_last_maintenance`
# since the raw data has no explicit "due date" field.
# NOTE: this is a documented assumption — tune it or replace it with a
# real SLA figure from your department docs if you get one.
MAINTENANCE_INTERVAL_DAYS = {
    "Engineering": 180,
    "S&T": 120,
    "TRD": 150,
}

SEVERITY_ORDER = {"routine": 0, "minor": 1, "moderate": 2, "severe": 3, "urgent": 4}

def load_raw():
    assets = pd.read_csv(
        DATA_DIR / "assets.csv",
        parse_dates=["install_date", "last_maintenance_date", "last_usfd_test_date"],
    )
    defects = pd.read_csv(
        DATA_DIR / "defects.csv",
        parse_dates=["reported_at"],
    )
    block_requests = pd.read_csv(
        DATA_DIR / "block_requests.csv",
        parse_dates=["requested_at"],
    )
    outcomes = pd.read_csv(
        DATA_DIR / "historical_outcomes.csv",
        parse_dates=["observed_at"],
    )
    sections = pd.read_csv(DATA_DIR / "sections.csv")
    signal_failures = pd.read_csv(
        DATA_DIR / "signal_failures.csv",
        parse_dates=["failure_timestamp", "restoration_timestamp"],
    )
    return assets, defects, block_requests, outcomes, sections, signal_failures


def build():
    assets, defects, block_requests, outcomes, sections, signal_failures = load_raw()

    # ---- base: one row per request, this is our snapshot moment ----
    df = block_requests.merge(
        outcomes[["request_id", "asset_id", "failed_within_30_days"]],
        on=["request_id", "asset_id"], how="inner"
    )
    df = df.merge(assets, on="asset_id", suffixes=("", "_asset"))
    # sections.csv has its own traffic_density_gmt too; asset-level one wins, keep section for context cols only
    df = df.merge(
        sections[["section_id", "zone", "train_count"]],
        on="section_id", how="left"
    )

    snapshot = df["requested_at"]

    # ---- Common features (asset-condition-known-at-snapshot) ----
    df["asset_age_days"] = (snapshot - df["install_date"]).dt.days
    df["days_since_last_maintenance"] = (snapshot - df["last_maintenance_date"]).dt.days
    df["days_since_usfd"] = (snapshot - df["last_usfd_test_date"]).dt.days  # NaN for non-Engineering, that's fine

    interval = df["department"].map(MAINTENANCE_INTERVAL_DAYS)
    df["days_overdue"] = (df["days_since_last_maintenance"] - interval).clip(lower=0)
    df["effective_age_days"] = df["asset_age_days"] * (df["traffic_density_gmt"] / 20.0) ** 0.6

    # ---- defect-history features, computed as-of the snapshot (no future defects allowed) ----
    def defect_history_for_row(asset_id, cutoff, defect_id_triggering):
        past = defects[(defects["asset_id"] == asset_id) & (defects["reported_at"] < cutoff)]
        hist_count = len(past)
        trig = defects[defects["defect_id"] == defect_id_triggering]
        trig_category = trig["defect_category"].iloc[0] if len(trig) else None
        trig_severity = trig["severity_text"].iloc[0] if len(trig) else None
        repeated = (past["defect_category"] == trig_category).sum() if trig_category else 0
        return hist_count, repeated, trig_severity, trig_category

    hist_counts, repeated_counts, severities, categories = [], [], [], []
    for row in df.itertuples():
        hc, rc, sev, cat = defect_history_for_row(row.asset_id, row.requested_at, row.defect_id)
        hist_counts.append(hc)
        repeated_counts.append(rc)
        severities.append(sev)
        categories.append(cat)

    df["historical_defect_count"] = hist_counts
    df["repeated_defect_count"] = repeated_counts
    df["severity"] = severities
    df["severity_rank"] = df["severity"].map(SEVERITY_ORDER)
    df["defect_category"] = categories

    # ---- S&T-specific: downtime / failure history as-of snapshot ----
    def st_history(asset_id, cutoff):
        past = signal_failures[(signal_failures["asset_id"] == asset_id) & (signal_failures["failure_timestamp"] < cutoff)]
        return len(past), past["downtime_minutes"].sum()

    st_freq, st_downtime = [], []
    for row in df.itertuples():
        if row.department == "S&T":
            f, d = st_history(row.asset_id, row.requested_at)
        else:
            f, d = np.nan, np.nan
        st_freq.append(f)
        st_downtime.append(d)
    df["failure_frequency"] = st_freq
    df["historical_downtime_minutes"] = st_downtime

    # ---- TRD-specific: flag if the triggering defect is a wire/OHE-condition category ----
    wire_categories = {"Contact wire wear beyond limit", "OHE sag beyond tolerance", "Dropper failure"}
    df["trd_wire_wear_flag"] = np.where(
        (df["department"] == "TRD") & (df["defect_category"].isin(wire_categories)), 1,
        np.where(df["department"] == "TRD", 0, np.nan)
    )

    # ---- final column selection (this IS your feature schema) ----
    feature_cols = [
        # identifiers (kept for traceability, drop before training)
        "request_id", "asset_id", "requested_at",
        # common
        "asset_age_days", "days_since_last_maintenance", "days_since_usfd",
        "days_overdue", "historical_defect_count", "repeated_defect_count",
        "severity_rank", "asset_type", "department", "criticality_class",
        "traffic_density_gmt", "track_geometry_index", "duration_minutes",
        "block_type", "train_count",
        # S&T
        "failure_frequency", "historical_downtime_minutes",
        # TRD
        "trd_wire_wear_flag",
        # label
        "failed_within_30_days",
        "effective_age_days",
    ]

    out = df[feature_cols].sort_values("requested_at").reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(out)} rows -> {OUT_PATH}")
    print(f"Positive rate: {out['failed_within_30_days'].mean():.4f}")
    print(out.isna().mean().round(2))
    return out


if __name__ == "__main__":
    build()
