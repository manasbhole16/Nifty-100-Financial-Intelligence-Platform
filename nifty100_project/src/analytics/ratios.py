import logging
import os

# Ensure output directory exists for the log
os.makedirs('output', exist_ok=True)

# Configure logging for edge cases
logging.basicConfig(
    filename='output/ratio_edge_cases.log', 
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_npm(net_profit, sales):
    """Calculates Net Profit Margin. Returns None if sales is 0."""
    if not sales or sales == 0:
        return None
    return (net_profit / sales) * 100

def calculate_opm(operating_profit, sales, reported_opm=None, company_id="Unknown"):
    """
    Calculates Operating Profit Margin.
    Cross-checks against reported OPM and logs a warning if difference > 1%.
    """
    if not sales or sales == 0:
        return None
    
    calculated_opm = (operating_profit / sales) * 100
    
    if reported_opm is not None:
        if abs(calculated_opm - reported_opm) > 1.0:
            logging.warning(
                f"OPM Mismatch [{company_id}]: Calculated {calculated_opm:.2f}%, "
                f"Reported {reported_opm:.2f}%"
            )
            
    return calculated_opm

def calculate_roe(net_profit, equity_capital, reserves):
    """Calculates Return on Equity. Returns None if total equity <= 0."""
    total_equity = equity_capital + reserves
    if total_equity <= 0:
        return None
    return (net_profit / total_equity) * 100

def calculate_roce(ebit, equity_capital, reserves, borrowings, broad_sector=None, sector_benchmark=None):
    """
    Calculates Return on Capital Employed.
    Note: For 'Financials' broad_sector, downstream evaluation should compare 
    this result against 'sector_benchmark' rather than the absolute threshold.
    """
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed == 0:
        return None
    
    roce = (ebit / capital_employed) * 100
    return roce

def calculate_roa(net_profit, total_assets):
    """Calculates Return on Assets. Returns None if total assets is 0."""
    if not total_assets or total_assets == 0:
        return None
    return (net_profit / total_assets) * 100