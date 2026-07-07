"""
Ratio Engine: Profitability, Leverage & Efficiency KPIs.
Sprint 2, Days 08-09 (Module 2, features 2.1-2.4) -- matches the exact
formulas in the authoritative Day-by-day sprint document.

All functions take plain floats (already extracted from a single
company-year row) and return a float, or None when the calculation is
undefined -- callers log these as edge cases (see populate_ratios.py).
"""

from typing import Optional


def _safe_div(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


# --------------------------------------------------------------------------
# Profitability Ratios (D08)
# --------------------------------------------------------------------------
def net_profit_margin(net_profit: float, sales: float) -> Optional[float]:
    """NPM (%) = Net Profit / Sales x 100. None if sales == 0."""
    if sales is None or sales == 0:
        return None
    return (net_profit / sales) * 100 if net_profit is not None else None


def operating_profit_margin(operating_profit: float, sales: float) -> Optional[float]:
    """OPM (%) = Operating Profit / Sales x 100. None if sales == 0."""
    if sales is None or sales == 0:
        return None
    return (operating_profit / sales) * 100 if operating_profit is not None else None


def opm_cross_check_mismatch(computed_opm: Optional[float], source_opm: Optional[float]) -> bool:
    """Day 08: cross-check computed OPM against the source opm_percentage
    field. Returns True (mismatch, should be logged) if the absolute
    difference exceeds 1 percentage point."""
    if computed_opm is None or source_opm is None:
        return False
    return abs(computed_opm - source_opm) > 1.0


def return_on_equity(net_profit: float, equity_capital: float, reserves: float) -> Optional[float]:
    """ROE (%) = Net Profit / (Equity Capital + Reserves) x 100.
    None if equity + reserves <= 0 (not just == 0 -- negative net worth
    makes ROE meaningless too)."""
    if equity_capital is None or reserves is None:
        return None
    shareholders_equity = equity_capital + reserves
    if shareholders_equity <= 0:
        return None
    return (net_profit / shareholders_equity) * 100 if net_profit is not None else None


def return_on_capital_employed(operating_profit: float, equity_capital: float, reserves: float, borrowings: float) -> Optional[float]:
    """ROCE (%) = EBIT / (Equity Capital + Reserves + Borrowings) x 100.

    Computed the same way for every company, including Financials --
    per Day 08, financial-sector companies get a *sector-relative
    benchmark* applied when interpreting the number (handled by the
    caller / is_financial_sector flag), not a different formula or a
    None value.
    """
    if equity_capital is None or reserves is None or borrowings is None:
        return None
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return (operating_profit / capital_employed) * 100 if operating_profit is not None else None


def return_on_assets(net_profit: float, total_assets: float) -> Optional[float]:
    """ROA (%) = Net Profit / Total Assets x 100. None if total_assets == 0."""
    if total_assets is None or total_assets == 0:
        return None
    return (net_profit / total_assets) * 100 if net_profit is not None else None


# --------------------------------------------------------------------------
# Leverage & Efficiency Ratios (D09)
# --------------------------------------------------------------------------
def debt_to_equity(borrowings: float, equity_capital: float, reserves: float) -> Optional[float]:
    """D/E = Borrowings / (Equity Capital + Reserves).
    Returns 0.0 (NOT None) if borrowings == 0 -- a debt-free company has
    a well-defined D/E of zero. Returns None only if the equity
    denominator itself is <= 0 (undefined / meaningless ratio)."""
    if equity_capital is None or reserves is None:
        return None
    shareholders_equity = equity_capital + reserves
    if shareholders_equity <= 0:
        return None
    if borrowings is None or borrowings == 0:
        return 0.0
    return borrowings / shareholders_equity


def high_leverage_flag(de_ratio: Optional[float], is_financial_sector: bool) -> bool:
    """Day 09: D/E > 5 AND company is NOT in the Financials sector."""
    if de_ratio is None or is_financial_sector:
        return False
    return de_ratio > 5


def interest_coverage_ratio(operating_profit: float, other_income: float, interest: float):
    """ICR = (Operating Profit + Other Income) / Interest Expense.

    Returns (icr_value, icr_label):
      - interest == 0 (or missing) -> (None, 'Debt Free')
      - otherwise                  -> (ratio, None)
    """
    if interest is None or interest == 0:
        return None, "Debt Free"
    ebit_plus_other_income = (operating_profit or 0) + (other_income or 0)
    return ebit_plus_other_income / interest, None


def icr_at_risk_flag(icr_value: Optional[float]) -> bool:
    """Day 09: ICR < 1.5 -- company may struggle to cover interest payments."""
    if icr_value is None:
        return False
    return icr_value < 1.5


def net_debt(borrowings: float, investments: float) -> Optional[float]:
    """Net Debt = Borrowings - Investments (investments used as the
    liquid-asset proxy per Day 09)."""
    if borrowings is None:
        return None
    return borrowings - (investments or 0)


def asset_turnover(sales: float, total_assets: float) -> Optional[float]:
    """Asset Turnover = Sales / Total Assets. None if total_assets == 0."""
    if total_assets is None or total_assets == 0:
        return None
    return sales / total_assets if sales is not None else None
