import sqlite3
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Ensure output directories exist
os.makedirs("reports", exist_ok=True)
os.makedirs("output", exist_ok=True)

def fetch_data(db_path="data/nifty100.db"):
    """Fetches the latest year financial metrics for all 92 companies."""
    conn = sqlite3.connect(db_path)
    
    # Query aligned precisely with your explicit table layout
    query = """
        SELECT 
            c.company_id,
            s.broad_sector, 
            f.return_on_equity_pct, 
            f.debt_to_equity, 
            f.revenue_cagr_5yr, 
            f.fcf_conversion_rate_pct, 
            f.operating_profit_margin_pct
        FROM companies c
        JOIN financial_ratios f ON c.company_id = f.company_id
        JOIN sectors s ON c.company_id = s.company_id
        WHERE f.year = (SELECT MAX(year) FROM financial_ratios)
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def run_clustering():
    print("Starting KMeans Clustering Process...")
    
    # 1. Load Data
    df = fetch_data()
    
    features = [
        'return_on_equity_pct', 
        'debt_to_equity', 
        'revenue_cagr_5yr', 
        'fcf_conversion_rate_pct', 
        'operating_profit_margin_pct'
    ]
    
    # 2. Impute missing values with sector median for each metric
    for feature in features:
        df[feature] = df.groupby('broad_sector')[feature].transform(
            lambda x: x.fillna(x.median())
        )
        # Fallback if an entire sector is missing a metric
        df[feature] = df[feature].fillna(df[feature].median())
        
    # 3. Apply StandardScaler to normalise features to zero mean and unit variance
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[features])
    
    # 4. Generate Elbow Plot (inertia vs k from 2 to 10)
    print("Generating Elbow Plot...")
    inertias = []
    k_range = range(2, 11)
    
    for k in k_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_temp.fit(scaled_data)
        inertias.append(kmeans_temp.inertia_)
        
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, inertias, marker='o', linestyle='--')
    plt.title('KMeans Clustering Elbow Plot')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.xticks(k_range)
    plt.grid(True)
    plt.savefig('reports/elbow_plot.png')
    plt.close()
    print("Elbow plot saved to reports/elbow_plot.png")
    
    # 5. Run KMeans with n_clusters=5
    print("Fitting KMeans model with k=5...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(scaled_data)
    
    # 6. Calculate distance from centroid
    distances = kmeans.transform(scaled_data)
    df['distance_from_centroid'] = distances.min(axis=1)
    
    # 7. Assign temporary cluster names (to be updated in Day 37)
    df['cluster_name'] = df['cluster_id'].apply(lambda x: f"Cluster {x}")
    
    # 8. Generate output/cluster_labels.csv
    output_columns = ['company_id', 'cluster_id', 'cluster_name', 'distance_from_centroid']
    output_df = df[output_columns]
    
    output_df.to_csv('output/cluster_labels.csv', index=False)
    print("Cluster labels generated and saved to output/cluster_labels.csv")

if __name__ == "__main__":
    run_clustering()