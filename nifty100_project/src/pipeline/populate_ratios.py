import sqlite3
import pandas as pd
import logging
import os
from src.analytics.ratios import (
    calculate_npm, calculate_opm, calculate_roe, calculate_roce, calculate_roa,
    calculate_debt_to_equity, calculate_icr, calculate_net_debt, calculate_asset_turnover
)
from src.analytics.cashflow_kpis import (
    calculate_fcf, calculate_cfo_quality_score, calculate_capex_intensity, classify_capital_allocation
)

DB_PATH = "nifty100_project/data/nifty100.db"

def setup_database():
    """Creates the financial_ratios table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the destination table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_ratios (
            company_id TEXT,
            year INTEGER,
            npm REAL,
            opm REAL,
            roe REAL,
            roce REAL,
            roa REAL,
            debt_to_equity REAL,
            high_leverage_flag BOOLEAN,
            icr REAL,
            icr_warning_flag BOOLEAN,
            net_debt REAL,
            asset_turnover REAL,
            fcf REAL,
            cfo_quality_score REAL,
            capex_intensity REAL,
            capital_allocation_pattern TEXT,
            PRIMARY KEY (company_id, year)
        )
    ''')
    conn.commit()
    return conn

def process_and_populate():
    """Reads raw data, computes KPIs, and writes to the financial_ratios table."""
    conn = setup_database()
    
    try:
        # 1. Extract raw data from Sprint 1 table (assuming it's named 'raw_financials')
        # Adjust column names based on your actual Sprint 1 schema
        df = pd.read_sql_query("SELECT * FROM companies", conn)
        
        results = []
        
        # 2. Iterate through each row and compute metrics
        for index, row in df.iterrows():
            cid = row.get('company_id', 'Unknown')
            sector = row.get('broad_sector', 'Unknown')
            
            # Profitability
            npm = calculate_npm(row.get('net_profit', 0), row.get('sales', 0))
            opm = calculate_opm(row.get('operating_profit', 0), row.get('sales', 0), row.get('reported_opm'), cid)
            roe = calculate_roe(row.get('net_profit', 0), row.get('equity_capital', 0), row.get('reserves', 0))
            roce = calculate_roce(row.get('ebit', 0), row.get('equity_capital', 0), row.get('reserves', 0), row.get('borrowings', 0), sector)
            roa = calculate_roa(row.get('net_profit', 0), row.get('total_assets', 0))
            
            # Leverage & Efficiency
            de_ratio, lev_flag = calculate_debt_to_equity(row.get('borrowings', 0), row.get('equity_capital', 0), row.get('reserves', 0), sector)
            icr, icr_label, icr_flag = calculate_icr(row.get('operating_profit', 0), row.get('other_income', 0), row.get('interest', 0))
            net_debt = calculate_net_debt(row.get('borrowings', 0), row.get('investments', 0))
            asset_to = calculate_asset_turnover(row.get('sales', 0), row.get('total_assets', 0))
            
            # Cash Flow
            fcf = calculate_fcf(row.get('cfo', 0), row.get('capex', 0))
            cfo_qual = calculate_cfo_quality_score(row.get('cfo', 0), row.get('net_profit', 0))
            capex_int = calculate_capex_intensity(row.get('capex', 0), row.get('sales', 0))
            cap_alloc = classify_capital_allocation(row.get('cfo', 0), row.get('cfi', 0), row.get('cff', 0))
            
            # Append to results
            results.append({
                'company_id': cid,
                'year': row.get('year'),
                'npm': npm,
                'opm': opm,
                'roe': roe,
                'roce': roce,
                'roa': roa,
                'debt_to_equity': de_ratio,
                'high_leverage_flag': lev_flag,
                'icr': icr,
                'icr_warning_flag': icr_flag,
                'net_debt': net_debt,
                'asset_turnover': asset_to,
                'fcf': fcf,
                'cfo_quality_score': cfo_qual,
                'capex_intensity': capex_int,
                'capital_allocation_pattern': cap_alloc
            })
            
        # 3. Load computed data back into the database
        results_df = pd.DataFrame(results)
        results_df.to_sql('financial_ratios', conn, if_exists='replace', index=False)
        print(f"Successfully populated financial_ratios table with {len(results_df)} rows.")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    process_and_populate()