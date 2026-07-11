import sqlite3
import pandas as pd
import os

def generate_peer_excel(db_path='data/nifty100.db', output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'peer_comparison.xlsx')

    # 1. Fetch data from our new table
    conn = sqlite3.connect(db_path)
    query = """
        SELECT c.company_name, p.peer_group_name, p.metric, p.percentile_rank
        FROM peer_percentiles p
        JOIN companies c ON p.company_id = c.company_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("❌ No data found in peer_percentiles table. Run peer.py first.")
        return

    # 2. Pivot the data so Metrics become columns and Companies become rows
    pivot_df = df.pivot_table(
        index=['company_name', 'peer_group_name'],
        columns='metric',
        values='percentile_rank'
    ).reset_index()

    # Define a mock benchmark company to highlight in Gold (as requested in DoD)
    benchmark_company = pivot_df['company_name'].iloc[0]

    # 3. Create the multi-sheet Excel file
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Define our custom visual styles
        median_format = workbook.add_format({'bold': True, 'bg_color': '#E0E0E0', 'top': 1})
        benchmark_format = workbook.add_format({'bg_color': '#FFD700', 'bold': True}) # Gold/Amber

        # Group the data by Sector to create the 11 separate sheets
        for sector, sector_df in pivot_df.groupby('peer_group_name'):
            # Excel sheet names can only be 31 characters long
            sheet_name = str(sector)[:31] 
            
            # Clean up the dataframe for export
            sheet_df = sector_df.drop(columns=['peer_group_name']).set_index('company_name')

            # DAY 19 REQUIREMENT: Add the 'PEER GROUP MEDIAN' row to the bottom
            medians = sheet_df.median()
            sheet_df.loc['PEER GROUP MEDIAN'] = medians

            # Write data to the specific sheet
            sheet_df.to_excel(writer, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]

            # Get dimensions for formatting
            num_rows = len(sheet_df)
            num_cols = len(sheet_df.columns)

            # DAY 19 REQUIREMENT: Apply Red-Yellow-Green Conditional Formatting
            worksheet.conditional_format(1, 1, num_rows - 1, num_cols, {
                'type': '3_color_scale',
                'min_color': '#FF9999', # Red (Low Percentile)
                'mid_color': '#FFFF99', # Yellow (Average)
                'max_color': '#99FF99'  # Green (Top Percentile)
            })

            # Format specific rows (Benchmark and Median)
            for row_num, company in enumerate(sheet_df.index):
                if company == benchmark_company:
                    worksheet.set_row(row_num + 1, cell_format=benchmark_format)
                elif company == 'PEER GROUP MEDIAN':
                    worksheet.set_row(row_num + 1, cell_format=median_format)
                    
            # Make the columns wide enough to read easily
            worksheet.set_column(0, 0, 35) # Company Name column
            worksheet.set_column(1, num_cols, 18) # Metric columns

    print(f"✅ SUCCESS: Formatted Excel report saved to {output_path}")
    print(f"   -> Contains {len(pivot_df['peer_group_name'].unique())} unique peer group sheets.")
    print(f"   -> Benchmark Company Highlighted: {benchmark_company}")

if __name__ == "__main__":
    print("\n🚀 Initializing Day 19 Peer Excel Generator...\n")
    generate_peer_excel()
