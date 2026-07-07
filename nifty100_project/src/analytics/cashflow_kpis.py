"""
Cash Flow KPIs & Capital Allocation Engine -- Sprint 2, Day 11 (Module 2,
features 2.6-2.7) -- rewritten to match the exact formulas and the
sign-based 8-pattern classifier from the authoritative sprint doc.
"""

from typing import Optional, List


# --------------------------------------------------------------------------
# Cash Flow KPIs (D11)
# --------------------------------------------------------------------------
def free_cash_flow(operating_activity: float, investing_activity: float) -> Optional[float]:
    """FCF (Rs Cr) = Cash from Operating Activities + Cash from Investing
    Activities. Negative values are allowed and meaningful (heavy
    investment years)."""
    if operating_activity is None or investing_activity is None:
        return None
    return operating_activity + investing_activity


def cfo_quality_score(cfo_pat_ratios: List[float]):
    """Day 11: CFO Quality Score = CFO/PAT ratio *averaged over the
    trailing up to 5 years* (years where PAT <= 0 are excluded from the
    average since the ratio is undefined for them).

    `cfo_pat_ratios` is the list of valid (PAT > 0) single-year CFO/PAT
    ratios for the trailing window, already filtered by the caller.

    Returns (score, label):
      score > 1.0        -> 'High Quality'
      0.5 <= score <= 1.0 -> 'Moderate'
      score < 0.5         -> 'Accrual Risk'
      no valid years      -> (None, None)
    """
    if not cfo_pat_ratios:
        return None, None
    score = sum(cfo_pat_ratios) / len(cfo_pat_ratios)
    if score > 1.0:
        label = "High Quality"
    elif score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return score, label


def single_year_cfo_pat_ratio(operating_activity: float, net_profit: float) -> Optional[float]:
    """One year's CFO/PAT ratio, used as an input to cfo_quality_score().
    None if PAT <= 0 (ratio undefined / not meaningful for a loss-making year)."""
    if net_profit is None or net_profit <= 0 or operating_activity is None:
        return None
    return operating_activity / net_profit


def capex_intensity(investing_activity: float, sales: float):
    """Day 11: CapEx Intensity (%) = abs(investing_activity) / Sales x 100.

    Returns (value, label):
      < 3%   -> 'Asset Light'
      3-8%   -> 'Moderate'
      > 8%   -> 'Capital Intensive'
    """
    if sales is None or sales == 0 or investing_activity is None:
        return None, None
    value = abs(investing_activity) / sales * 100
    if value < 3:
        label = "Asset Light"
    elif value <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return value, label


def fcf_conversion_rate(fcf: Optional[float], operating_profit: float) -> Optional[float]:
    """FCF Conversion Rate (%) = FCF / Operating Profit x 100.
    None if operating_profit == 0 (or FCF itself undefined)."""
    if fcf is None or operating_profit is None or operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100


# --------------------------------------------------------------------------
# Capital Allocation Pattern Classifier (D11) -- sign-based, 8 patterns
# --------------------------------------------------------------------------
CAPITAL_ALLOCATION_PATTERNS = [
    "Reinvestor",
    "Shareholder Returns",
    "Liquidating Assets",
    "Distress Signal",
    "Growth Funded by Debt",
    "Cash Accumulator",
    "Pre-Revenue",
    "Mixed",
]


def _sign(value: Optional[float]) -> str:
    if value is None:
        return "?"
    return "+" if value >= 0 else "-"


def classify_capital_allocation(
    cfo: Optional[float],
    cfi: Optional[float],
    cff: Optional[float],
    cfo_pat_quality_score: Optional[float] = None,
) -> str:
    """Day 11: classify into one of 8 patterns based purely on the sign
    of (CFO, CFI, CFF), per the authoritative sprint doc:

        (+,-,-)                          -> Reinvestor
        (+,-,-) with high CFO/PAT quality -> Shareholder Returns
        (+,+,-)                          -> Liquidating Assets
        (-,+,+)                          -> Distress Signal
        (-,-,+)                          -> Growth Funded by Debt
        (+,+,+)                          -> Cash Accumulator
        (-,-,-)                          -> Pre-Revenue
        (+,-,+)                          -> Mixed
        anything else (e.g. missing data, unlisted -+- combo) -> Mixed

    "High CFO/PAT quality" (tie-break for (+,-,-)) is read as
    cfo_pat_quality_score > 1.0 (the 'High Quality' CFO Quality Score
    threshold from the same day's spec).
    """
    signs = (_sign(cfo), _sign(cfi), _sign(cff))

    if signs == ("+", "-", "-"):
        if cfo_pat_quality_score is not None and cfo_pat_quality_score > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    if signs == ("+", "+", "-"):
        return "Liquidating Assets"
    if signs == ("-", "+", "+"):
        return "Distress Signal"
    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"
    if signs == ("+", "+", "+"):
        return "Cash Accumulator"
    if signs == ("-", "-", "-"):
        return "Pre-Revenue"
    if signs == ("+", "-", "+"):
        return "Mixed"
    return "Mixed"  # unlisted / missing-data combos (e.g. -+- or any '?')
