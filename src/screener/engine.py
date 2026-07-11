import sqlite3
import pandas as pd
import yaml
import numpy as np
import os

class ScreenerEngine:
    def __init__(self, db_path='data/nifty100.db', config_path='config/screener_config.yaml'):
        self.db_path = db_path
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
            
        self.column_map = {
            'roe': 'return_on_equity_pct',
            'roce': 'return_on_capital_employed_pct',
            'de': 'debt_to_equity',
            'fcf': 'free_cash_flow_cr',
            'interest_coverage_ratio': 'interest_coverage_ratio',
            'rev_cagr_5yr': 'revenue_cagr_5yr',
            'pat_cagr_5yr': 'pat_cagr_5yr',
            'pe': 'pe_ratio', 
            'pb': 'pb_ratio',
            'div_yield': 'dividend_yield_pct'
        }

    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT c.*, f.* FROM financial_ratios f
                LEFT JOIN companies c ON f.company_id = c.company_id
                INNER JOIN (
                    SELECT company_id, MAX(year) as max_year 
                    FROM financial_ratios GROUP BY company_id
                ) latest ON f.company_id = latest.company_id AND f.year = latest.max_year
            """
            df = pd.read_sql_query(query, conn)
            df = df.loc[:, ~df.columns.duplicated()]
            conn.close()
            
            # Market Data Simulator
            np.random.seed(42) 
            if 'pe_ratio' not in df.columns: df['pe_ratio'] = np.random.uniform(10, 35, size=len(df))
            if 'pb_ratio' not in df.columns: df['pb_ratio'] = np.random.uniform(1, 6, size=len(df))
            if 'dividend_yield_pct' not in df.columns: df['dividend_yield_pct'] = np.random.uniform(0, 3, size=len(df))
            if 'revenue_cr' not in df.columns: df['revenue_cr'] = np.random.uniform(3000, 15000, size=len(df))
            return df
        except Exception as e:
            print(f"Database Error: {e}")
            return pd.DataFrame()

    def compute_composite_score(self, df):
        """DAY 17: P10/P90 Winsorization and Weighted 0-100 Scoring"""
        score = pd.Series(0.0, index=df.index)
        total_weight = 0.0

        # Metrics where HIGHER is better
        positive_metrics = {
            'return_on_equity_pct': 0.15,
            'return_on_capital_employed_pct': 0.10,
            'revenue_cagr_5yr': 0.10,
            'pat_cagr_5yr': 0.10
        }

        for col, weight in positive_metrics.items():
            if col in df.columns:
                # P10/P90 Winsorization (Caps outliers)
                p10, p90 = df[col].quantile(0.10), df[col].quantile(0.90)
                clipped = df[col].clip(lower=p10, upper=p90)
                
                # Min-Max Scaling (0 to 100)
                min_val, max_val = clipped.min(), clipped.max()
                if max_val > min_val:
                    scaled = (clipped - min_val) / (max_val - min_val) * 100
                else:
                    scaled = 50.0
                
                score += scaled * weight
                total_weight += weight

        # Metrics where LOWER is better (Debt)
        if 'debt_to_equity' in df.columns:
            col = 'debt_to_equity'
            p10, p90 = df[col].quantile(0.10), df[col].quantile(0.90)
            clipped = df[col].clip(lower=p10, upper=p90)
            min_val, max_val = clipped.min(), clipped.max()
            if max_val > min_val:
                # INVERT THE SCORE (Less debt = higher score)
                scaled = 100 - ((clipped - min_val) / (max_val - min_val) * 100)
            else:
                scaled = 50.0
            
            score += scaled * 0.10
            total_weight += 0.10

        # Final Score Normalization (out of 100)
        df['composite_quality_score'] = (score / total_weight) if total_weight > 0 else 0.0
        return df

    def apply_filters(self, filter_dict):
        df = self.load_data()
        if df.empty: return df

        # Apply scoring before filtering so relative percentiles use the whole universe
        df = self.compute_composite_score(df)

        if 'interest_coverage_ratio' in df.columns:
            df['interest_coverage_ratio'] = df['interest_coverage_ratio'].replace('Debt Free', np.inf)
            df['interest_coverage_ratio'] = pd.to_numeric(df['interest_coverage_ratio'], errors='coerce').fillna(np.inf)

        for metric_key, threshold in filter_dict.items():
            is_min = metric_key.endswith('_min')
            is_max = metric_key.endswith('_max')
            base_metric = metric_key.rsplit('_', 1)[0] if (is_min or is_max) else metric_key
            col_name = self.column_map.get(base_metric, base_metric)

            if col_name in df.columns:
                df = df.dropna(subset=[col_name])
                if base_metric == 'de' and is_max and 'is_financial_sector' in df.columns:
                    is_financial = df['is_financial_sector'] == 1 
                    meets_de = df[col_name] <= threshold
                    df = df[meets_de | is_financial]
                elif base_metric == 'de' and threshold <= 0.01:
                    df = df[df[col_name] <= 0.01] 
                else:
                    if is_min: df = df[df[col_name] >= threshold]
                    elif is_max: df = df[df[col_name] <= threshold]

        return df.sort_values(by='composite_quality_score', ascending=False)

    def export_to_excel(self, results_dict, output_dir='output'):
        """DAY 17: Multi-sheet Excel Export"""
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, 'screener_output.xlsx')
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for preset_name, df in results_dict.items():
                if not df.empty:
                    # Keep a clean subset of columns for the report
                    export_cols = ['company_name', 'broad_sector', 'composite_quality_score', 
                                   'return_on_equity_pct', 'debt_to_equity', 'pe_ratio']
                    export_cols = [c for c in export_cols if c in df.columns]
                    
                    sheet_name = preset_name[:31] # Excel sheets max 31 chars
                    df[export_cols].round(2).to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"\n✅ Excel Report Generated: {file_path}")

if __name__ == "__main__":
    print("\n🚀 Initializing Day 17 Screener Engine (Scoring & Export)...\n")
    engine = ScreenerEngine()
    presets = engine.config.get('presets', {})
    
    all_results = {}
    
    for preset_name, thresholds in presets.items():
        results = engine.apply_filters(thresholds)
        all_results[preset_name] = results
        
        count = len(results)
        status = "✅" if 5 <= count <= 50 else "⚠️"
        
        print(f"{status} [{preset_name.upper().replace('_', ' ')}] -> {count} Companies Passed")
        
        if not results.empty:
            display_cols = ['company_name', 'composite_quality_score', 'return_on_equity_pct']
            display_cols = [c for c in display_cols if c in results.columns]
            print(results[display_cols].head(3).round(2).to_string(index=False))
        print("-" * 65)

    # Trigger the Excel Generation
    engine.export_to_excel(all_results)
