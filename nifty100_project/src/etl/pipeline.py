"""
End-to-end ETL orchestration for the Nifty 100 Financial Intelligence
Platform. Sprint 1 (Days 01-07) deliverable.

Flow: load_all_data() -> run_validations() -> SQLite (10 core/aux tables)
      -> output/load_audit.csv + output/validation_failures.csv

Run directly:  python -m src.etl.pipeline
"""

import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.etl.database import engine, Base
from src.etl import models  # noqa: F401  (registers ORM tables with Base)
from src.etl.loader import load_all_data
from src.etl.validator import run_validations
from src.etl.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

# (source_dict_key, sql_table_name, columns_to_drop_before_insert)
TABLE_MAP = [
    ("companies.xlsx", "companies", []),
    ("profitandloss.xlsx", "profitandloss", ["id"]),
    ("balancesheet.xlsx", "balancesheet", ["id"]),
    ("cashflow.xlsx", "cashflow", ["id"]),
    ("analysis.xlsx", "analysis", ["id"]),
    ("documents.xlsx", "documents", ["id"]),
    ("prosandcons.xlsx", "prosandcons", ["id"]),
    ("sectors.xlsx", "sectors", ["id"]),
    ("market_cap.xlsx", "market_cap", ["id"]),
    ("stock_prices.xlsx", "stock_prices", ["id"]),
    ("peer_groups.xlsx", "peer_groups", ["id"]),
    ("financial_ratios.xlsx", "financial_ratios_reference", ["id"]),
]

# The "official" 10 tables per Module 1 spec (used for row-count reporting)
PRIMARY_TABLES = [
    "companies", "profitandloss", "balancesheet", "cashflow", "analysis",
    "documents", "prosandcons", "sectors", "market_cap", "stock_prices",
]


def _insert_dataframe(df: pd.DataFrame, table_name: str, drop_cols: list) -> int:
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    if df.empty:
        logger.warning(f"No rows to insert for {table_name} (empty DataFrame after cleaning).")
        return 0
    df.to_sql(table_name, engine, if_exists="append", index=False)
    return len(df)


def run_full_pipeline():
    pipeline_start = time.time()
    logger.info("=" * 60)
    logger.info("Starting full ETL pipeline run.")
    print("\U0001f680 Starting Nifty 100 ETL Pipeline...")

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 1. LOAD all 12 source files
    raw = load_all_data()
    rows_in = {name: len(df) for name, df in raw.items()}

    # 2. VALIDATE against all 16 DQ rules
    cleaned, failures_df = run_validations(raw)
    rows_out_by_key = {name: len(df) for name, df in cleaned.items()}

    # 3. Persist validation_failures.csv
    failures_path = OUTPUT_DIR / "validation_failures.csv"
    failures_df.to_csv(failures_path, index=False)
    logger.info(f"Wrote {len(failures_df)} DQ findings to {failures_path}")
    print(f"\U0001f4dd Wrote {len(failures_df)} DQ findings to {failures_path}")

    # 4. Build schema fresh (idempotent create_all; drop first for a clean rerun)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("\u2705 Schema created successfully! data/nifty100.db is ready.")

    # 5. Load each cleaned DataFrame into its SQLite table
    audit_rows = []
    for file_key, table_name, drop_cols in TABLE_MAP:
        df = cleaned[file_key]
        t0 = time.time()
        rows_written = _insert_dataframe(df, table_name, drop_cols)
        runtime_s = round(time.time() - t0, 4)
        rejected = rows_in[file_key] - rows_written
        audit_rows.append({
            "table": table_name,
            "source_file": file_key,
            "rows_in": rows_in[file_key],
            "rows_out": rows_written,
            "rejected": rejected,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "runtime_s": runtime_s,
        })
        logger.info(f"Loaded {table_name}: {rows_written} rows written, {rejected} rejected ({runtime_s}s)")
        print(f"\u2705 {table_name}: {rows_written} rows written ({rejected} rejected)")

    audit_df = pd.DataFrame(audit_rows)
    audit_path = OUTPUT_DIR / "load_audit.csv"
    audit_df.to_csv(audit_path, index=False)

    total_runtime = round(time.time() - pipeline_start, 2)
    n_critical = (failures_df["severity"] == "CRITICAL").sum() if not failures_df.empty else 0
    n_warning = (failures_df["severity"] == "WARNING").sum() if not failures_df.empty else 0

    print("\n" + "=" * 60)
    print(f"\u2705 PIPELINE COMPLETE in {total_runtime}s")
    print(f"   Tables loaded : {len(TABLE_MAP)} ({len(PRIMARY_TABLES)} primary + {len(TABLE_MAP) - len(PRIMARY_TABLES)} auxiliary)")
    print(f"   CRITICAL flags: {n_critical}")
    print(f"   WARNING flags : {n_warning}")
    print(f"   load_audit.csv          -> {audit_path}")
    print(f"   validation_failures.csv -> {failures_path}")
    print("=" * 60)

    logger.info(f"Pipeline complete in {total_runtime}s. CRITICAL={n_critical}, WARNING={n_warning}")
    return audit_df, failures_df


if __name__ == "__main__":
    run_full_pipeline()
