import pandas as pd
from pathlib import Path

def normalize_ticker(ticker):
    """Strips whitespace and converts to uppercase NSE ticker."""
    if pd.isna(ticker):
        return ticker
    return str(ticker).strip().upper()

def normalize_year(year_str):
    """Standardizes 'Mar-23' format to '2023-03'."""
    if pd.isna(year_str):
        return year_str
    
    year_str = str(year_str).strip()
    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    
    try:
        parts = year_str.split('-')
        if len(parts) == 2:
            month_abbr = parts[0][:3]
            # UPGRADE: Only transform if it's a real month AND the year is a number
            if month_abbr in month_map and parts[1].isdigit():
                month = month_map[month_abbr]
                year_val = parts[1]
                
                # Handle 2-digit years (e.g., 23 -> 2023)
                if len(year_val) == 2:
                    year_val = f"20{year_val}"
                    
                return f"{year_val}-{month}"
    except Exception:
        pass # If parsing fails, return original string for DQ flagging
        
    return year_str

def load_core_data(data_dir="data/raw"):
    """Loads all 7 core Excel files using header=1 and normalizes keys."""
    core_files = [
        'companies.xlsx', 'profitandloss.xlsx', 'balancesheet.xlsx', 
        'cashflow.xlsx', 'analysis.xlsx', 'documents.xlsx', 'prosandcons.xlsx'
    ]
    
    dataframes = {}
    base_path = Path(data_dir)
    
    for file_name in core_files:
        file_path = base_path / file_name
        if file_path.exists():
            # Load with header=1 to skip metadata row
            df = pd.read_excel(file_path, header=1)
            
            # Normalize Tickers
            if 'company_id' in df.columns:
                df['company_id'] = df['company_id'].apply(normalize_ticker)
            elif 'id' in df.columns and file_name == 'companies.xlsx':
                df['id'] = df['id'].apply(normalize_ticker)
                
            # Normalize Years
            if 'year' in df.columns:
                df['year'] = df['year'].apply(normalize_year)
                
            dataframes[file_name] = df
            print(f"✅ Loaded {file_name}: {df.shape[0]} rows")
        else:
            print(f"❌ Missing file: {file_name}")
            
    return dataframes

if __name__ == "__main__":
    # Quick test run
    dfs = load_core_data()