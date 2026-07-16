import pandas as pd
import sqlite3
import os

def classify_capital_allocation():
    conn = sqlite3.connect('data/nifty100.db')
    # Fetch sign of cash flows
    query = "SELECT company_id, cfo_sign, cfi_sign, cff_sign FROM financial_ratios"
    df = pd.read_sql_query(query, conn)
    conn.close()

    def get_pattern_label(row):
        # Maps sign (+/-) combination to a business strategy label
        pattern = (row['cfo_sign'], row['cfi_sign'], row['cff_sign'])
        mapping = {
            ('+', '-', '-'): 'Growth/Dividend Payer',
            ('+', '-', '+'): 'Leveraged Grower',
            ('+', '+', '-'): 'Cash Accumulator/Asset Liquidation',
            ('-', '-', '-'): 'Distressed/Funding Dependent'
            # Add other combinations as per your specific business requirements
        }
        return mapping.get(pattern, 'Unknown/Transition')

    df['capital_allocation_pattern'] = df.apply(get_pattern_label, axis=1)
    
    os.makedirs('output', exist_ok=True)
    df.to_csv('output/capital_allocation.csv', index=False)
    print("Capital Allocation Mapping complete. Saved to output/capital_allocation.csv")

if __name__ == "__main__":
    classify_capital_allocation()