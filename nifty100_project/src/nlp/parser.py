import pandas as pd
import re
import os

def parse_analysis_data(input_file='data/analysis.xlsx'):
    # Regex pattern: (\d+) matches years, ([\d.]+) matches percentage
    # Added slight flexibility for spacing with \s*
    pattern = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")
    
    # Load analysis data, skipping the title row
    df = pd.read_excel(input_file, skiprows=1)
    
    parsed_data = []
    failures = []

    # The specific columns we need to parse
    metrics_to_check = [
        'compounded_sales_growth', 
        'compounded_profit_growth', 
        'stock_price_cagr', 
        'roe'
    ]

    for index, row in df.iterrows():
        company_id = row['company_id']
        
        # Go through each of the 4 metric columns
        for metric in metrics_to_check:
            cell_text = str(row[metric])
            
            # Skip empty/NaN cells
            if cell_text.lower() != 'nan' and cell_text.strip() != '':
                match = pattern.search(cell_text)
                
                if match:
                    parsed_data.append({
                        'company_id': company_id,
                        'metric_type': metric,
                        'period_years': int(match.group(1)),
                        'value_pct': float(match.group(2))
                    })
                else:
                    failures.append({
                        'company_id': company_id,
                        'metric_type': metric,
                        'failed_text': cell_text
                    })

    # Ensure output directory exists just in case
    os.makedirs('output', exist_ok=True)

    # Save outputs
    pd.DataFrame(parsed_data).to_csv('output/analysis_parsed.csv', index=False)
    pd.DataFrame(failures).to_csv('output/parse_failures.csv', index=False)
    
    print(f"Parsing complete. Successfully parsed {len(parsed_data)} metrics.")
    if failures:
        print(f"Logged {len(failures)} format mismatches to output/parse_failures.csv")

if __name__ == "__main__":
    parse_analysis_data()