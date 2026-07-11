import sqlite3
import pandas as pd
import yaml
import numpy as np

class ScreenerEngine:
    def __init__(self, db_path='data/nifty100.db', config_path='config/screener_config.yaml'):
        self.db_path = db_path
        
        # Load the configuration thresholds
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def load_data(self):
        """Loads the most recent financial ratios from SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Fetch the most recent year's data
            query = """
                SELECT * FROM financial_ratios 
                WHERE year = (SELECT MAX(year) FROM financial_ratios)
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Database Error: {e}")
            return pd.DataFrame()

    def apply_filters(self, filter_dict):
        """Applies dynamic thresholds and handles SPRINT 3 edge cases."""
        df = self.load_data()
        if df.empty:
            return df

        # Edge Case 1: ICR Filter - Treat "Debt Free" as infinity
        if 'interest_coverage_ratio' in df.columns:
            df['interest_coverage_ratio'] = df['interest_coverage_ratio'].replace('Debt Free', np.inf)
            df['interest_coverage_ratio'] = pd.to_numeric(df['interest_coverage_ratio'], errors='coerce').fillna(np.inf)

        # Apply Thresholds dynamically
        for metric_key, threshold in filter_dict.items():
            
            # Map the config key (e.g., 'roe_min') to the database column (e.g., 'roe')
            is_min = metric_key.endswith('_min')
            is_max = metric_key.endswith('_max')
            col_name = metric_key.rsplit('_', 1)[0] if (is_min or is_max) else metric_key

            if col_name not in df.columns:
                # Handle special alias for D/E
                if metric_key == 'de_max' and 'debt_to_equity' in df.columns:
                    # Edge Case 2: D/E Filter - Automatically skip Financials sector
                    is_financial = df['broad_sector'].str.lower().isin(['financials', 'financial services'])
                    meets_de = df['debt_to_equity'] <= threshold
                    df = df[meets_de | is_financial]
                else:
                    continue
            else:
                # Standard Min/Max Filtering
                if is_min:
                    df = df[df[col_name] >= threshold]
                elif is_max:
                    df = df[df[col_name] <= threshold]

        # Day 15 Requirement: Add composite_quality_score column
        df['composite_quality_score'] = 0.0
        
        # Return sorted dataframe
        return df.sort_values(by='composite_quality_score', ascending=False)

if __name__ == "__main__":
    print("Initializing Screener Engine...")
    engine = ScreenerEngine()
    
    print("\nRunning Day 15 Core Engine Test...")
    test_thresholds = engine.config.get('test_filters', {})
    
    results = engine.apply_filters(test_thresholds)
    
    print(f"Total Companies Passing Core Filters: {len(results)}")
    if not results.empty:
        display_cols = ['company_name', 'broad_sector', 'roe', 'debt_to_equity', 'interest_coverage_ratio', 'composite_quality_score']
        display_cols = [c for c in display_cols if c in results.columns]
        
        print(results[display_cols].head())