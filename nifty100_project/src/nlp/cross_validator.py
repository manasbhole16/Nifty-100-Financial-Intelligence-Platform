import pandas as pd
import sqlite3
import os

def validate_parsed_cagr(db_path='data/nifty100.db'):
    print("Starting CAGR cross-validation...")
    
    # Load parsed data
    parsed_df = pd.read_csv('output/analysis_parsed.csv')
    
    # Load computed metrics from the Ratio Engine
    conn = sqlite3.connect(db_path)
    # UPDATED SQL: Using the correct column names from your database
    query = "SELECT company_id, return_on_equity_pct, revenue_cagr_5yr, pat_cagr_5yr FROM financial_ratios"
    ratios_df = pd.read_sql_query(query, conn)
    conn.close()

    divergence_alerts = []

    for _, row in parsed_df.iterrows():
        comp_id = row['company_id']
        metric = row['metric_type']
        parsed_val = row['value_pct']
        
        # Match with computed DB values
        # Note: 'pat_cagr_5yr' is the profit CAGR
        col_map = {
            'roe': 'return_on_equity_pct',
            'compounded_sales_growth': 'revenue_cagr_5yr',
            'compounded_profit_growth': 'pat_cagr_5yr'
        }
        
        db_col = col_map.get(metric)
        
        if db_col and comp_id in ratios_df['company_id'].values:
            computed_val = ratios_df.loc[ratios_df['company_id'] == comp_id, db_col].values[0]
            
            if pd.notnull(computed_val):
                diff = abs(parsed_val - computed_val)
                if diff > 5.0:
                    divergence_alerts.append({
                        'company_id': comp_id,
                        'metric': metric,
                        'parsed_value': parsed_val,
                        'computed_value': computed_val,
                        'divergence': diff
                    })

    # Output divergence > 5% for manual review
    if divergence_alerts:
        pd.DataFrame(divergence_alerts).to_csv('output/cagr_divergence_alerts.csv', index=False)
        print(f"Validation complete. {len(divergence_alerts)} edge cases flagged in output/cagr_divergence_alerts.csv")
    else:
        print("Validation complete. All parsed data aligns with the Ratio Engine (<5% variance).")

if __name__ == "__main__":
    validate_parsed_cagr()