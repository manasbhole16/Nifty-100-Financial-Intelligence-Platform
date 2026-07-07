"""
Excel loader for the Nifty 100 Financial Intelligence Platform.

Sprint 1 (Days 01-02, 05) deliverable. Loads the 7 core Excel files
(header=1 -- row 0 is a metadata/title row, row 1 is the real header)
plus the 5 supplementary files (header=0 -- clean headers already).

Per the project specification (Section 5 / 6 Dataset Catalogue):
  - Core files:        companies, profitandloss, balancesheet, cashflow,
                        analysis, documents, prosandcons
  - Supplementary:      sectors, stock_prices, market_cap,
                        financial_ratios (reference only), peer_groups

company_id is normalised (strip + uppercase) on every table that has it.
year fields on the annual time-series tables are normalised via
normalize_year() to the 'YYYY-MM' convention.
"""

from pathlib import Path
import pandas as pd

from src.etl.normaliser import normalize_ticker, normalize_year
from src.etl.logger import get_logger

logger = get_logger(__name__)

# Core files use header=1 (row 0 is a metadata/title row)
CORE_FILES = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
]

# Supplementary files use header=0 (clean headers already present)
SUPPLEMENTARY_FILES = [
    "sectors.xlsx",
    "stock_prices.xlsx",
    "market_cap.xlsx",
    "financial_ratios.xlsx",
    "peer_groups.xlsx",
]

# company_id column name varies: companies.xlsx uses 'id', others use 'company_id'
_TICKER_COLUMN_BY_FILE = {
    "companies.xlsx": "id",
}

# Tables that carry a per-row financial-year label needing normalize_year()
_YEAR_COLUMN_BY_FILE = {
    "profitandloss.xlsx": "year",
    "balancesheet.xlsx": "year",
    "cashflow.xlsx": "year",
}


def _load_one(base_path: Path, file_name: str, header: int) -> pd.DataFrame:
    file_path = base_path / file_name
    if not file_path.exists():
        logger.error(f"Missing file: {file_path}")
        print(f"\u274c Missing file: {file_path}")
        return pd.DataFrame()

    df = pd.read_excel(file_path, header=header)

    # Normalise tickers
    ticker_col = _TICKER_COLUMN_BY_FILE.get(file_name, "company_id")
    if ticker_col in df.columns:
        df[ticker_col] = df[ticker_col].apply(normalize_ticker)

    # Normalise year labels (P&L / BS / CF only)
    year_col = _YEAR_COLUMN_BY_FILE.get(file_name)
    if year_col and year_col in df.columns:
        df[year_col] = df[year_col].apply(normalize_year)

    logger.info(f"Loaded {file_name}: {df.shape[0]} rows, {df.shape[1]} cols (header={header})")
    print(f"\u2705 Loaded {file_name}: {df.shape[0]} rows")
    return df


def load_core_data(data_dir="data/raw") -> dict:
    """Loads all 7 core Excel files using header=1 and normalizes keys."""
    base_path = Path(data_dir)
    dataframes = {}
    for file_name in CORE_FILES:
        dataframes[file_name] = _load_one(base_path, file_name, header=1)
    return dataframes


def load_supplementary_data(data_dir="data/supporting") -> dict:
    """Loads all 5 supplementary Excel files using header=0."""
    base_path = Path(data_dir)
    dataframes = {}
    for file_name in SUPPLEMENTARY_FILES:
        dataframes[file_name] = _load_one(base_path, file_name, header=0)
    return dataframes


def load_all_data(core_dir="data/raw", supplementary_dir="data/supporting") -> dict:
    """Loads all 12 source files (7 core + 5 supplementary) in one call."""
    dataframes = load_core_data(core_dir)
    dataframes.update(load_supplementary_data(supplementary_dir))
    return dataframes


if __name__ == "__main__":
    # Quick test run
    dfs = load_all_data()
    print(f"\nLoaded {len(dfs)} files total.")
