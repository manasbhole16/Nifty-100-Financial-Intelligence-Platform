def calculate_fcf(cfo, capex):
    """
    Calculates Free Cash Flow (FCF).
    Formula: Cash Flow from Operations (CFO) - Capital Expenditures.
    Note: Assumes capex is provided as a positive absolute value. 
    If source data has capex as negative (outflow), use cfo + capex.
    """
    return cfo - abs(capex)

def calculate_cfo_quality_score(cfo, pat):
    """
    Calculates CFO Quality Score (CFO / PAT).
    A ratio > 1 indicates high-quality earnings (cash-backed).
    Returns None if PAT is 0.
    """
    if not pat or pat == 0:
        return None
    return cfo / pat

def calculate_capex_intensity(capex, revenue):
    """
    Calculates Capital Expenditure Intensity (CapEx / Revenue).
    Returns None if Revenue is 0.
    """
    if not revenue or revenue == 0:
        return None
    return (abs(capex) / revenue) * 100

def classify_capital_allocation(cfo, cfi, cff):
    """
    Classifies the company's capital allocation strategy based on the 
    signs (+ or -) of Operations, Investing, and Financing cash flows.
    """
    sign_cfo = "+" if cfo >= 0 else "-"
    sign_cfi = "+" if cfi >= 0 else "-"
    sign_cff = "+" if cff >= 0 else "-"

    pattern = f"{sign_cfo}{sign_cfi}{sign_cff}"

    classifier_map = {
        "+--": "Mature Reinvestor / Shareholder Returns", # Generates cash, invests, pays dividends/debt
        "+-+": "Growth Expansion (Externally Funded)",    # Generates cash, invests heavily, borrows to fund gap
        "++-": "Asset Liquidation / Deleveraging",        # Generates cash, sells assets, pays down debt
        "+++": "Cash Hoarding / Restructuring",           # Generates cash, sells assets, raises cash (rare)
        "--+": "High-Growth Burn / Start-up",             # Burns cash on ops, invests heavily, relies on funding
        "-++": "Distress (Selling Assets to Fund Ops)",   # Burns cash, forced to sell assets and borrow to survive
        "-+-": "Shrinking / Forced Liquidation",          # Burns cash, sells assets just to pay off debt
        "---": "Severe Distress (Cash Burn)"              # Bleeding cash across all three fronts
    }

    return classifier_map.get(pattern, "Unknown Pattern")