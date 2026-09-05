import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Check backend/.env"
    )

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_DIR = BASE_DIR / "dataset" / "extracted" / "railblock_dataset"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ============================================================
# HELPERS
# ============================================================

def read_csv(filename: str) -> pd.DataFrame:
    path = DATASET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    print(f"\nReading {filename}...")

    df = pd.read_csv(path)

    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")

    return df


def test_connection():
    print("\nTesting Supabase connection...")

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    print("✓ Supabase connection successful")


# ============================================================
# 1. SECTIONS
# ============================================================

def load_sections():

    print("\n" + "=" * 60)
    print("1. SECTIONS")
    print("=" * 60)

    df = read_csv("sections.csv")

    df = df.rename(
        columns={
            "lat": "latitude",
            "lon": "longitude",
        }
    )

    columns = [
        "section_id",
        "from_station",
        "to_station",
        "zone",
        "latitude",
        "longitude",
        "traffic_density_gmt",
        "train_count",
    ]

    df = df[columns].copy()

    df = df.drop_duplicates(subset=["section_id"])

    # Remove sections that are already present.
    with engine.connect() as conn:
        existing = pd.read_sql(
            text("SELECT section_id FROM sections"),
            conn,
        )

    existing_ids = set(existing["section_id"].astype(str))

    df["section_id"] = df["section_id"].astype(str)

    df = df[~df["section_id"].isin(existing_ids)]

    if df.empty:
        print("✓ No new sections to insert")
        return

    df.to_sql(
        "sections",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(f"✓ Inserted {len(df):,} sections")


# ============================================================
# 2. ASSETS
# ============================================================

def load_assets():

    print("\n" + "=" * 60)
    print("2. ASSETS")
    print("=" * 60)

    df = read_csv("assets.csv")

    # Existing legacy asset codes
    with engine.connect() as conn:
        existing = pd.read_sql(
            text("SELECT asset_code FROM assets"),
            conn,
        )

        sections = pd.read_sql(
            text("""
                SELECT
                    section_id,
                    from_station,
                    to_station
                FROM sections
            """),
            conn,
        )

    existing_codes = set(
        existing["asset_code"].astype(str)
    )

    section_lookup = sections.set_index("section_id")

    rows = []

    for _, row in df.iterrows():

        asset_code = str(row["asset_id"])

        if asset_code in existing_codes:
            continue

        section_id = str(row["section_id"])

        section_name = None

        if section_id in section_lookup.index:

            section_row = section_lookup.loc[section_id]

            from_station = section_row["from_station"]
            to_station = section_row["to_station"]

            if pd.notna(from_station) and pd.notna(to_station):
                section_name = (
                    f"{from_station} - {to_station}"
                )

        rows.append(
            {
                "asset_code": asset_code,
                "asset_type": row["asset_type"],
                "section": section_name,
                "section_id": section_id,
                "install_date": row["install_date"],
                "last_maintenance_date": row[
                    "last_maintenance_date"
                ],
                "last_usfd_test_date": row[
                    "last_usfd_test_date"
                ],
                "criticality_class": row[
                    "criticality_class"
                ],
                "traffic_density_gmt": row[
                    "traffic_density_gmt"
                ],
                "track_geometry_index": row[
                    "track_geometry_index"
                ],
            }
        )

    if not rows:
        print("✓ No new assets to insert")
        return

    insert_df = pd.DataFrame(rows)

    insert_df.to_sql(
        "assets",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(f"✓ Inserted {len(insert_df):,} assets")


# ============================================================
# ASSET ID MAPPING
# ============================================================

def get_asset_map():

    print("\nBuilding asset ID mapping...")

    with engine.connect() as conn:

        assets = pd.read_sql(
            text("""
                SELECT id, asset_code
                FROM assets
            """),
            conn,
        )

    asset_map = dict(
        zip(
            assets["asset_code"].astype(str),
            assets["id"],
        )
    )

    print(
        f"✓ {len(asset_map):,} asset mappings available"
    )

    return asset_map


# ============================================================
# 3. DEFECTS
# ============================================================

def load_defects(asset_map):

    print("\n" + "=" * 60)
    print("3. DEFECTS")
    print("=" * 60)

    df = read_csv("defects.csv")

    df["asset_id"] = (
        df["asset_id"]
        .astype(str)
        .map(asset_map)
    )

    missing = df["asset_id"].isna().sum()

    if missing:
        print(
            f"⚠ Skipping {missing:,} defects "
            "with missing assets"
        )

    df = df.dropna(subset=["asset_id"])

    df = df.rename(
        columns={
            "asset_id": "asset_id",
        }
    )

    columns = [
        "defect_id",
        "asset_id",
        "source_system",
        "defect_category",
        "severity_text",
        "free_text_note",
        "reported_at",
    ]

    df = df[columns]

    with engine.connect() as conn:
        existing = pd.read_sql(
            text("SELECT defect_id FROM defects"),
            conn,
        )

    existing_ids = set(
        existing["defect_id"].astype(str)
    )

    df["defect_id"] = df["defect_id"].astype(str)

    df = df[
        ~df["defect_id"].isin(existing_ids)
    ]

    if df.empty:
        print("✓ No new defects to insert")
        return

    df.to_sql(
        "defects",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(f"✓ Inserted {len(df):,} defects")


# ============================================================
# 4. SIGNAL FAILURES
# ============================================================

def load_signal_failures(asset_map):

    print("\n" + "=" * 60)
    print("4. SIGNAL FAILURES")
    print("=" * 60)

    df = read_csv("signal_failures.csv")

    df["asset_id"] = (
        df["asset_id"]
        .astype(str)
        .map(asset_map)
    )

    missing = df["asset_id"].isna().sum()

    if missing:
        print(
            f"⚠ Skipping {missing:,} signal failures "
            "with missing assets"
        )

    df = df.dropna(subset=["asset_id"])

    columns = [
        "asset_id",
        "failure_timestamp",
        "failure_type",
        "restoration_timestamp",
        "downtime_minutes",
        "restored_by",
    ]

    df = df[columns]

    # Remove duplicate failure events.
    df = df.drop_duplicates(
        subset=[
            "asset_id",
            "failure_timestamp",
        ]
    )

    # Convert database IDs to integers.
    df["asset_id"] = df["asset_id"].astype(int)

    # Read existing events.
    with engine.connect() as conn:
        existing = pd.read_sql(
            text("""
                SELECT
                    asset_id,
                    failure_timestamp
                FROM signal_failures
            """),
            conn,
        )

    if not existing.empty:

        existing_keys = set(
            zip(
                existing["asset_id"],
                existing["failure_timestamp"].astype(str),
            )
        )

        df["event_key"] = list(
            zip(
                df["asset_id"],
                df["failure_timestamp"].astype(str),
            )
        )

        df = df[
            ~df["event_key"].isin(existing_keys)
        ]

        df = df.drop(columns=["event_key"])

    if df.empty:
        print("✓ No new signal failures to insert")
        return

    df.to_sql(
        "signal_failures",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(
        f"✓ Inserted {len(df):,} signal failures"
    )


# ============================================================
# 5. TRAIN SCHEDULE
# ============================================================

def load_train_schedule():

    print("\n" + "=" * 60)
    print("5. TRAIN SCHEDULE")
    print("=" * 60)

    df = read_csv("train_schedule.csv")

    columns = [
        "train_no",
        "train_name",
        "train_type",
        "section_id",
        "from_station",
        "to_station",
        "entry_time",
        "exit_time",
    ]

    df = df[columns]

    df = df.dropna(
        subset=[
            "train_no",
            "section_id",
            "entry_time",
            "exit_time",
        ]
    )

    df = df.drop_duplicates(
        subset=[
            "train_no",
            "section_id",
            "entry_time",
            "exit_time",
        ]
    )

    with engine.connect() as conn:
        existing = pd.read_sql(
            text("""
                SELECT
                    train_no,
                    section_id,
                    entry_time,
                    exit_time
                FROM train_schedule
            """),
            conn,
        )

    if not existing.empty:

        existing_keys = set(
            zip(
                existing["train_no"].astype(str),
                existing["section_id"].astype(str),
                existing["entry_time"].astype(str),
                existing["exit_time"].astype(str),
            )
        )

        df["key"] = list(
            zip(
                df["train_no"].astype(str),
                df["section_id"].astype(str),
                df["entry_time"].astype(str),
                df["exit_time"].astype(str),
            )
        )

        df = df[
            ~df["key"].isin(existing_keys)
        ]

        df = df.drop(columns=["key"])

    if df.empty:
        print("✓ No new train schedule rows")
        return

    df.to_sql(
        "train_schedule",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    print(
        f"✓ Inserted {len(df):,} train schedule rows"
    )


# ============================================================
# 6. HISTORICAL BLOCK REQUESTS
# ============================================================

def load_historical_block_requests(asset_map):

    print("\n" + "=" * 60)
    print("6. HISTORICAL BLOCK REQUESTS")
    print("=" * 60)

    df = read_csv("block_requests.csv")

    df["asset_id"] = (
        df["asset_id"]
        .astype(str)
        .map(asset_map)
    )

    missing = df["asset_id"].isna().sum()

    if missing:
        print(
            f"⚠ Skipping {missing:,} historical "
            "block requests with missing assets"
        )

    df = df.dropna(subset=["asset_id"])

    columns = [
        "request_id",
        "defect_id",
        "asset_id",
        "department",
        "block_type",
        "duration_minutes",
        "requested_at",
    ]

    df = df[columns]

    df["asset_id"] = df["asset_id"].astype(int)

    df = df.drop_duplicates(
        subset=["request_id"]
    )

    with engine.connect() as conn:
        existing = pd.read_sql(
            text("""
                SELECT request_id
                FROM historical_block_requests
            """),
            conn,
        )

    existing_ids = set(
        existing["request_id"].astype(str)
    )

    df["request_id"] = df["request_id"].astype(str)

    df = df[
        ~df["request_id"].isin(existing_ids)
    ]

    if df.empty:
        print(
            "✓ No new historical block requests"
        )
        return

    df.to_sql(
        "historical_block_requests",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(
        f"✓ Inserted {len(df):,} historical block requests"
    )


# ============================================================
# 7. HISTORICAL OUTCOMES
# ============================================================

def load_historical_outcomes(asset_map):

    print("\n" + "=" * 60)
    print("7. HISTORICAL OUTCOMES")
    print("=" * 60)

    df = read_csv("historical_outcomes.csv")

    df["asset_id"] = (
        df["asset_id"]
        .astype(str)
        .map(asset_map)
    )

    missing = df["asset_id"].isna().sum()

    if missing:
        print(
            f"⚠ Skipping {missing:,} outcomes "
            "with missing assets"
        )

    df = df.dropna(subset=["asset_id"])

    columns = [
        "asset_id",
        "request_id",
        "observed_at",
        "failed_within_30_days",
    ]

    df = df[columns]

    df["asset_id"] = df["asset_id"].astype(int)

    # Convert target safely to boolean.
    df["failed_within_30_days"] = (
        df["failed_within_30_days"]
        .astype(str)
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
            }
        )
    )

    df = df.dropna(
        subset=["failed_within_30_days"]
    )

    df = df.drop_duplicates(
        subset=[
            "asset_id",
            "request_id",
        ]
    )

    with engine.connect() as conn:
        existing = pd.read_sql(
            text("""
                SELECT
                    asset_id,
                    request_id
                FROM historical_outcomes
            """),
            conn,
        )

    if not existing.empty:

        existing_keys = set(
            zip(
                existing["asset_id"],
                existing["request_id"].astype(str),
            )
        )

        df["key"] = list(
            zip(
                df["asset_id"],
                df["request_id"].astype(str),
            )
        )

        df = df[
            ~df["key"].isin(existing_keys)
        ]

        df = df.drop(columns=["key"])

    if df.empty:
        print("✓ No new historical outcomes")
        return

    df.to_sql(
        "historical_outcomes",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(
        f"✓ Inserted {len(df):,} historical outcomes"
    )


# ============================================================
# VERIFICATION
# ============================================================

def verify_counts():

    print("\n" + "=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)

    tables = [
        "sections",
        "assets",
        "defects",
        "signal_failures",
        "train_schedule",
        "historical_block_requests",
        "historical_outcomes",
    ]

    with engine.connect() as conn:

        for table in tables:

            count = conn.execute(
                text(
                    f"SELECT COUNT(*) FROM {table}"
                )
            ).scalar()

            print(
                f"{table:30} {count:>8,}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("       RAILBLOCK AI DATASET LOADER")
    print("=" * 60)

    print(
        f"\nDataset directory:\n{DATASET_DIR}"
    )

    if not DATASET_DIR.exists():
        raise RuntimeError(
            f"Dataset directory does not exist:\n"
            f"{DATASET_DIR}"
        )

    test_connection()

    load_sections()
    load_assets()

    asset_map = get_asset_map()

    load_defects(asset_map)
    load_signal_failures(asset_map)
    load_train_schedule()
    load_historical_block_requests(asset_map)
    load_historical_outcomes(asset_map)

    verify_counts()

    print("\n" + "=" * 60)
    print("✓ DATASET LOAD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()