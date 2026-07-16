# src/analytics/cashflow_kpis.py

CAPITAL_ALLOCATION_PATTERNS = [
    "Reinvestor", "Shareholder Returns", "Liquidating Assets", 
    "Distress Signal", "Growth Funded by Debt", "Cash Accumulator", 
    "Pre-Revenue", "Mixed"
]

def free_cash_flow(cfo, capex):
    if cfo is None or capex is None:
        return None
    return cfo + capex

def cfo_quality_score(ratios):
    if not ratios:
        return None, None
    avg = sum(ratios) / len(ratios)
    if avg >= 1.0:
        return avg, "High Quality"
    elif avg >= 0.5:
        return avg, "Moderate"
    return avg, "Accrual Risk"

def single_year_cfo_pat_ratio(cfo, pat):
    if pat is None or pat <= 0:
        return None
    return cfo / pat

def capex_intensity(capex, sales):
    if sales is None or sales == 0:
        return None, None
    value = abs(capex / sales) * 100
    
    # Adjusted logic: check for the highest threshold first
    if value >= 10.0:
        return value, "Capital Intensive"
    elif value >= 5.0:
        return value, "Moderate"
    else:
        return value, "Asset Light"

def fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100

def classify_capital_allocation(cfo, capex, financing, cfo_pat_quality_score=0.5):
    # Logic to classify based on sign patterns of (CFO, Capex, Financing)
    try:
        if cfo > 0 and capex < 0 and financing < 0:
            return "Reinvestor" if cfo_pat_quality_score < 1.0 else "Shareholder Returns"
        if cfo > 0 and capex > 0 and financing < 0:
            return "Liquidating Assets"
        if cfo < 0 and capex > 0 and financing > 0:
            return "Distress Signal"
        if cfo < 0 and capex < 0 and financing > 0:
            return "Growth Funded by Debt"
        if cfo > 0 and capex > 0 and financing > 0:
            return "Cash Accumulator"
        if cfo < 0 and capex < 0 and financing < 0:
            return "Pre-Revenue"
        return "Mixed"
    except:
        return "Mixed"