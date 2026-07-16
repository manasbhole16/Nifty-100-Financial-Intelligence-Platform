import sqlite3
import pandas as pd
import numpy as np
import os
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
# pyrefly: ignore [missing-import]
from scipy.stats import zscore

# Ensure output directories exist
os.makedirs("reports", exist_ok=True)
os.makedirs("output", exist_ok=True)

def fetch_sprint6_data(db_path="data/nifty100.db"):
    """Fetches a broader set of 10 KPIs + sector for profiling and correlation."""
    conn = sqlite3.connect(db_path)
    query = """
        SELECT 
            c.company_id,
            s.broad_sector,
            f.net_profit_margin_pct,
            f.operating_profit_margin_pct,
            f.return_on_equity_pct,
            f.return_on_capital_employed_pct,
            f.return_on_assets_pct,
            f.debt_to_equity,
            f.interest_coverage_ratio,
            f.revenue_cagr_5yr,
            f.capex_intensity_pct,
            f.fcf_conversion_rate_pct
        FROM companies c
        JOIN financial_ratios f ON c.company_id = f.company_id
        JOIN sectors s ON c.company_id = s.company_id
        WHERE f.year = (SELECT MAX(year) FROM financial_ratios)
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def run_profiling_and_stats():
    print("Starting Day 37 Cluster Profiling & Financial Statistics...")
    
    # 1. Load Core Financial Data and Cluster Labels
    df_financials = fetch_sprint6_data()
    df_labels = pd.read_csv("output/cluster_labels.csv")
    
    # Merge cluster IDs into our comprehensive financial dataframe
    df = pd.merge(df_financials, df_labels[['company_id', 'cluster_id']], on='company_id')
    
    clustering_features = [
        'return_on_equity_pct', 
        'debt_to_equity', 
        'revenue_cagr_5yr', 
        'fcf_conversion_rate_pct', 
        'operating_profit_margin_pct'
    ]
    
    # Impute missing values with sector median for baseline security
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            df[col] = df.groupby('broad_sector')[col].transform(lambda x: x.fillna(x.median()))
            df[col] = df[col].fillna(df[col].median())

    # 2. Profile Clusters to determine Archetype mappings
    print("Profiling clusters to assign descriptive names...")
    cluster_profiles = df.groupby('cluster_id')[clustering_features].mean()
    
    # Dynamically rank and assign names based on return profile and leverage characteristics
    archetype_map = {}
    for clus_id, row in cluster_profiles.iterrows():
        if row['return_on_equity_pct'] > 20 and row['debt_to_equity'] < 0.5:
            archetype_map[clus_id] = "High-Quality Compounders"
        elif row['debt_to_equity'] > 2.0:
            archetype_map[clus_id] = "Highly Leveraged / Financials"
        elif row['revenue_cagr_5yr'] > 15:
            archetype_map[clus_id] = "Aggressive Growth Engines"
        elif row['operating_profit_margin_pct'] > 25:
            archetype_map[clus_id] = "High Margin Defensive Monopolies"
        else:
            archetype_map[clus_id] = "Value / Moderate Compounders"
            
    # Update cluster_labels.csv with the correct profiled names
    df_labels['cluster_name'] = df_labels['cluster_id'].map(archetype_map)
    df_labels.to_csv("output/cluster_labels.csv", index=False)
    print("Successfully mapped archetypes and updated output/cluster_labels.csv")

    # 3. Generate Pearson Correlation Heatmap for 10 KPIs
    print("Generating Pearson Correlation Heatmap...")
    kpis_10 = [
        'net_profit_margin_pct', 'operating_profit_margin_pct', 'return_on_equity_pct',
        'return_on_capital_employed_pct', 'return_on_assets_pct', 'debt_to_equity',
        'interest_coverage_ratio', 'revenue_cagr_5yr', 'capex_intensity_pct', 'fcf_conversion_rate_pct'
    ]
    corr_matrix = df[kpis_10].corr(method='pearson')
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Pearson Correlation Heatmap of 10 Core Financial KPIs")
    plt.tight_layout()
    plt.savefig("reports/correlation_heatmap.png")
    plt.close()
    print("Saved correlation heatmap to reports/correlation_heatmap.png")

    # 4. Outlier Detection (Z-Score > 3 boundary)
    print("Generating Outlier Report...")
    outlier_rows = []
    for kpi in kpis_10:
        # Calculate standard normal z-scores
        df[f'z_{kpi}'] = zscore(df[kpi])
        outliers = df[df[f'z_{kpi}'].abs() > 3]
        for _, row in outliers.iterrows():
            outlier_rows.append({
                'company_id': row['company_id'],
                'field': kpi,
                'value': row[kpi],
                'z_score': row[f'z_{kpi}']
            })
            
    df_outliers = pd.DataFrame(outlier_rows)
    df_outliers.to_csv("output/outlier_report.csv", index=False)
    print(f"Outlier report generated with {len(df_outliers)} anomalies inside output/outlier_report.csv")

    # 5. Descriptive Portfolio Percentiles (P10 to P90)
    print("Generating Descriptive Portfolio Stats...")
    stats_rows = []
    for kpi in kpis_10:
        stats_rows.append({
            'kpi': kpi,
            'P10': np.percentile(df[kpi], 10),
            'P25': np.percentile(df[kpi], 25),
            'P50_Median': np.percentile(df[kpi], 50),
            'P75': np.percentile(df[kpi], 75),
            'P90': np.percentile(df[kpi], 90)
        })
    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv("output/portfolio_stats.csv", index=False)
    print("Descriptive statistics exported to output/portfolio_stats.csv")

if __name__ == "__main__":
    run_profiling_and_stats()