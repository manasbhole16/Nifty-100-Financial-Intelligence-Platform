"""
CAGR Engine -- Sprint 2, Day 10 (Module 2, feature 2.5).

Computes CAGR for Revenue, PAT and EPS across 3yr/5yr/10yr windows.
Every non-normal outcome is tagged with one of 5 explicit flag strings
(matching the authoritative sprint doc exactly), stored in a separate
*_flag column alongside the CAGR value so downstream consumers can tell
"no growth" apart from "not computable, and here's why".
"""

from typing import Optional, Tuple, List

CAGR_WINDOWS = (3, 5, 10)

FLAG_DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
FLAG_TURNAROUND = "TURNAROUND"
FLAG_BOTH_NEGATIVE = "BOTH_NEGATIVE"
FLAG_ZERO_BASE = "ZERO_BASE"
FLAG_INSUFFICIENT = "INSUFFICIENT"


def compute_cagr(begin_value: Optional[float], end_value: Optional[float], num_years: int) -> Tuple[Optional[float], Optional[str]]:
    """Returns (cagr_pct, flag). flag is None when the CAGR was computed
    normally; otherwise one of the 6 documented edge cases:

      - missing begin/end value or n <= 0  -> (None, 'INSUFFICIENT')
      - zero base                          -> (None, 'ZERO_BASE')
      - Positive -> Negative                -> (None, 'DECLINE_TO_LOSS')
      - Negative -> Positive                -> (None, 'TURNAROUND')
      - Negative -> Negative                -> (None, 'BOTH_NEGATIVE')
      - Positive -> Positive                -> (cagr, None)
    """
    if begin_value is None or end_value is None or num_years is None or num_years <= 0:
        return None, FLAG_INSUFFICIENT

    if begin_value == 0:
        return None, FLAG_ZERO_BASE

    if begin_value > 0 and end_value <= 0:
        return None, FLAG_DECLINE_TO_LOSS

    if begin_value < 0 and end_value > 0:
        return None, FLAG_TURNAROUND

    if begin_value < 0 and end_value <= 0:
        return None, FLAG_BOTH_NEGATIVE

    # begin_value > 0 and end_value > 0
    cagr = ((end_value / begin_value) ** (1.0 / num_years) - 1) * 100
    return cagr, None


def cagr_for_window(
    sorted_years: List[str],
    values_by_year: dict,
    latest_year: str,
    window: int,
) -> Tuple[Optional[float], Optional[str]]:
    """Looks up the value `window` years before `latest_year` in a
    company's own sorted year list (so it still works correctly when a
    company is missing some years in the middle) and computes CAGR."""
    if latest_year not in sorted_years:
        return None, FLAG_INSUFFICIENT

    latest_idx = sorted_years.index(latest_year)
    begin_idx = latest_idx - window
    if begin_idx < 0:
        return None, FLAG_INSUFFICIENT  # not enough history for this window

    begin_year = sorted_years[begin_idx]
    begin_value = values_by_year.get(begin_year)
    end_value = values_by_year.get(latest_year)

    return compute_cagr(begin_value, end_value, window)


def compute_all_cagr_windows(sorted_years: List[str], values_by_year: dict, latest_year: str) -> dict:
    """Returns {'cagr_3yr': v, 'cagr_3yr_flag': f, 'cagr_5yr': v, ...}
    for a single metric (Revenue, PAT, or EPS), one value+flag pair per
    window."""
    result = {}
    for window in CAGR_WINDOWS:
        value, flag = cagr_for_window(sorted_years, values_by_year, latest_year, window)
        result[f"cagr_{window}yr"] = value
        result[f"cagr_{window}yr_flag"] = flag
    return result
