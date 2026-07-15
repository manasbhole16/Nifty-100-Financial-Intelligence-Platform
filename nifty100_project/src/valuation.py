import pandas as pd
import numpy as np
import os

def run_valuation_engine():
    print("⚙️ Initializing N100 Valuation Engine...")

    # 1. Generate core financial dataset
    # (Using self-contained data to ensure it runs perfectly without prior sprint files)
    data = {
        'ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'BHARTIAIRTEL', 'INFY', 'ICICIBANK', 'ITC', 'SBIN'],
        'company_name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Bharti Airtel', 'Infosys', 'ICICI Bank', 'ITC Limited', 'State Bank of India'],
        'sector': ['Energy', 'Technology', 'Financials', 'Telecommunication', 'Technology', 'Financials', 'Consumer Goods', 'Financials'],
        'market_cap': [1850000, 1420000, 1150000, 950000, 680000, 820000, 520000, 480000],
        'pe_ratio': [26.4, 28.1, 19.5, 45.2, 24.3, 17.8, 22.4, 11.2],
        'free_cash_flow': [75000, 42000, 35000, 18000, 25000, 31000, 16000, 22000]
    }
    df = pd.DataFrame(data)

    # 2. Calculate FCF Yield
    df['fcf_yield'] = (df['free_cash_flow'] / df['market_cap']) * 100

    # 3. Calculate Sector Median P/E
    sector_medians = df.groupby('sector')['pe_ratio'].median().reset_index()
    sector_medians.rename(columns={'pe_ratio': 'sector_median_pe'}, inplace=True)
    
    # Merge the medians back into the main dataframe
    df = pd.merge(df, sector_medians, on='sector', how='left')

    # 4. Apply Valuation Flags (Discount, Fair, Overvalued)
    def determine_flag(row):
        if row['pe_ratio'] > (row['sector_median_pe'] * 1.2):
            return "Overvalued 🔴"
        elif row['pe_ratio'] < (row['sector_median_pe'] * 0.8):
            return "Discounted 🟢"
        else:
            return "Fair Value 🟡"

    df['valuation_flag'] = df.apply(determine_flag, axis=1)

    # 5. Format and Export the Results
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    excel_path = os.path.join(output_dir, "valuation_summary.xlsx")
    csv_path = os.path.join(output_dir, "valuation_flags.csv")

    # Reorder columns for clean reporting
    final_cols = ['ticker', 'company_name', 'sector', 'pe_ratio', 'sector_median_pe', 'fcf_yield', 'valuation_flag']
    final_df = df[final_cols]

    final_df.to_excel(excel_path, index=False)
    final_df.to_csv(csv_path, index=False)

    print(f"✅ Valuation analysis complete!")
    print(f"📁 Files exported to:\n - {excel_path}\n - {csv_path}")
    print("\n--- Summary Output ---")
    print(final_df[['ticker', 'valuation_flag', 'fcf_yield']])

if __name__ == "__main__":
    run_valuation_engine()