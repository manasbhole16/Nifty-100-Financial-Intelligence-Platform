import sqlite3
import pandas as pd
import numpy as np

class PeerEngine:
    def __init__(self, db_path='data/nifty100.db'):
        self.db_path = db_path
        
        self.metrics = {
            'ROE': 'return_on_equity_pct',
            'ROCE': 'return_on_capital_employed_pct',
            'Net Profit Margin': 'net_profit_margin_pct',
            'Debt to Equity': 'debt_to_equity',
            'Free Cash Flow': 'free_cash_flow_cr',
            'PAT CAGR 5yr': 'pat_cagr_5yr',
            'Revenue CAGR 5yr': 'revenue_cagr_5yr',
            'EPS CAGR 5yr': 'eps_cagr_5yr',
            'Interest Coverage': 'interest_coverage_ratio',
            'Asset Turnover': 'asset_turnover'
        }

    def load_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT c.company_id, c.company_name, f.* FROM financial_ratios f
                LEFT JOIN companies c ON f.company_id = c.company_id
                INNER JOIN (
                    SELECT company_id, MAX(year) as max_year 
                    FROM financial_ratios GROUP BY company_id
                ) latest ON f.company_id = latest.company_id AND f.year = latest.max_year
            """
            df = pd.read_sql_query(query, conn)
            df = df.loc[:, ~df.columns.duplicated()]
            conn.close()
            
            # Peer Group Simulator
            peer_groups = [
                'IT Services', 'FMCG', 'Financial Services', 'Automobile',
                'Pharmaceuticals', 'Metals & Mining', 'Oil & Gas', 'Consumer Durables',
                'Telecommunication', 'Power', 'Construction'
            ]
            np.random.seed(42) 
            if not df.empty:
                df['peer_group'] = np.random.choice(peer_groups, size=len(df))
            
            return df
        except Exception as e:
            print(f"Database Error: {e}")
            return pd.DataFrame()

    def compute_percentiles(self, df):
        results = []
        
        if 'interest_coverage_ratio' in df.columns:
            df['interest_coverage_ratio'] = df['interest_coverage_ratio'].replace('Debt Free', np.inf)
            df['interest_coverage_ratio'] = pd.to_numeric(df['interest_coverage_ratio'], errors='coerce')

        for peer_group, group_df in df.groupby('peer_group'):
            for metric_name, col_name in self.metrics.items():
                if col_name in group_df.columns:
                    valid_data = group_df[['company_id', 'company_name', 'year', col_name]].dropna().copy()
                    if valid_data.empty: continue
                        
                    ranks = valid_data[col_name].rank(pct=True)
                    
                    if metric_name == 'Debt to Equity':
                        ranks = 1.0 - valid_data[col_name].rank(pct=True, ascending=True)
                        
                    valid_data['percentile_rank'] = ranks * 100 
                    valid_data['metric'] = metric_name
                    valid_data['peer_group_name'] = peer_group
                    valid_data.rename(columns={col_name: 'value'}, inplace=True)
                    
                    results.append(valid_data[['company_id', 'peer_group_name', 'metric', 'value', 'percentile_rank', 'year']])
                    
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()

    def save_to_database(self, percentiles_df):
        if percentiles_df.empty: return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peer_percentiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT,
                peer_group_name TEXT,
                metric TEXT,
                value REAL,
                percentile_rank REAL,
                year INTEGER,
                UNIQUE(company_id, metric, year)
            )
        """)
        
        cursor.execute("DELETE FROM peer_percentiles")
        percentiles_df.to_sql('peer_percentiles', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("\n🚀 Initializing Day 18 Peer Analytics Engine...\n")
    engine = PeerEngine()
    
    df = engine.load_data()
    percentiles_df = engine.compute_percentiles(df)
    
    if not percentiles_df.empty:
        engine.save_to_database(percentiles_df)
        print(f"✅ Successfully saved {len(percentiles_df)} percentile records to database.")
        
        # DYNAMIC PREVIEW: Grab the very first group and metric that successfully computed
        sample_group = percentiles_df['peer_group_name'].iloc[0]
        sample_metric = percentiles_df['metric'].iloc[0]
        
        print(f"\n📊 [PREVIEW] {sample_group} - {sample_metric} Ranks:")
        preview = percentiles_df[(percentiles_df['peer_group_name'] == sample_group) & (percentiles_df['metric'] == sample_metric)]
        
        conn = sqlite3.connect(engine.db_path)
        names = pd.read_sql("SELECT company_id, company_name FROM companies", conn)
        preview = pd.merge(preview, names, on='company_id')
        
        print(preview[['company_name', 'metric', 'value', 'percentile_rank']].sort_values(by='percentile_rank', ascending=False).round(2).to_string(index=False))
    else:
        print("⚠️ No percentiles could be calculated.")
    print("-" * 65)
