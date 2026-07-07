"""
Normalisation helpers used across the ETL pipeline.

Day 02 deliverable (Sprint 1): normalize_ticker() and normalize_year().
Extracted into their own module so both loader.py and validator.py can
import them without a circular dependency, and so they are easy to unit
test in isolation (see tests/etl/test_normalise.py).
"""

import re
import pandas as pd

# Matches 'Mar-23', 'Dec 2012', 'Sep-2024', 'TTM' etc.
_MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}

YEAR_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def normalize_ticker(ticker):
    """Strips whitespace and converts to uppercase NSE ticker.

    DQ-08: company_id = company_id.strip().upper(); length 2-12 chars.
    Returns None unchanged (never coerces missing tickers to a string).
    """
    if pd.isna(ticker):
        return ticker
    return str(ticker).strip().upper()


def normalize_year(year_str):
    """Standardises financial-year labels to 'YYYY-MM'.

    Handles both hyphen ('Mar-23') and space ('Dec 2012') separators,
    2-digit and 4-digit years, and passes through values it cannot
    parse (e.g. 'TTM') so DQ-07 can flag them explicitly rather than
    silently dropping data.
    """
    if pd.isna(year_str):
        return year_str

    year_str = str(year_str).strip()

    # Normalise separator: 'Dec 2012' -> 'Dec-2012'
    normalised = re.sub(r"\s+", "-", year_str)

    try:
        parts = normalised.split("-")
        if len(parts) == 2:
            month_abbr = parts[0][:3].title()
            year_val = parts[1]
            if month_abbr in _MONTH_MAP and year_val.isdigit():
                month = _MONTH_MAP[month_abbr]
                if len(year_val) == 2:
                    year_val = f"20{year_val}"
                return f"{year_val}-{month}"
    except Exception:
        pass  # If parsing fails, return original string for DQ-07 to flag

    return year_str


def is_valid_year_format(value) -> bool:
    """DQ-07: after normalize_year(), value must match r'^\\d{4}-\\d{2}$'."""
    if pd.isna(value):
        return False
    return bool(YEAR_PATTERN.match(str(value)))


def is_valid_ticker_format(value) -> bool:
    """DQ-08 length check: normalised ticker must be 2-12 characters."""
    if pd.isna(value):
        return False
    return 2 <= len(str(value)) <= 12
