import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

def generate_radar_charts(db_path='data/nifty100.db', output_dir='reports/radar_charts'):
    # Create the reports folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    query = """
        SELECT c.company_name, p.peer_group_name, p.metric, p.percentile_rank 
        FROM peer_percentiles p 
        JOIN companies c ON p.company_id = c.company_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("❌ No data found in peer_percentiles table.")
        return

    # Calculate Peer Group Medians
    medians = df.groupby(['peer_group_name', 'metric'])['percentile_rank'].median().reset_index()
    medians.rename(columns={'percentile_rank': 'median_rank'}, inplace=True)

    # Merge medians back to the main dataframe
    df = pd.merge(df, medians, on=['peer_group_name', 'metric'])

    # To keep the demo fast, let's generate charts for the first 5 unique companies
    companies = df['company_name'].unique()[:5]

    print(f"📊 Generating Radar Charts for {len(companies)} sample companies...\n")

    for company in companies:
        company_data = df[df['company_name'] == company]
        peer_group = company_data['peer_group_name'].iloc[0]
        
        categories = company_data['metric'].tolist()
        N = len(categories)
        
        if N < 3:
            continue # Need at least 3 metrics to make a polygon
            
        # Values
        values = company_data['percentile_rank'].tolist()
        median_values = company_data['median_rank'].tolist()
        
        # Close the circle for the plot
        values += values[:1]
        median_values += median_values[:1]
        
        # Calculate angle for each axis
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]
        
        # Initialize the spider plot
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # Draw one axe per variable
        plt.xticks(angles[:-1], categories, color='black', size=9)
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["25th", "50th", "75th", "100th"], color="grey", size=8)
        plt.ylim(0, 100)
        
        # Plot Company Data (Blue)
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=company, color='#1f77b4')
        ax.fill(angles, values, '#1f77b4', alpha=0.25)
        
        # Plot Median Data (Red Dashed)
        ax.plot(angles, median_values, linewidth=2, linestyle='dashed', label=f"{peer_group} Median", color='#d62728')
        
        plt.title(f"Peer Percentile Radar: {company}", size=15, weight='bold', y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
        
        # Clean filename and save
        safe_name = company.replace(' ', '_').replace('/', '_').replace('\\n', '')
        filepath = os.path.join(output_dir, f"{safe_name}_radar.png")
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        
        print(f"✅ Saved: {filepath}")

if __name__ == "__main__":
    print("\n🚀 Initializing Day 20 Visual Data Engine...\n")
    generate_radar_charts()
    print("\nDone! Check your 'reports/radar_charts' folder.")
