import pandas as pd

def validate_company_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data Quality (DQ) Rules for the Companies dataset.
    Returns a cleaned DataFrame safe for database insertion.
    """
    print("🛡️ Running Data Quality (DQ) Checks...")
    initial_count = len(df)

    # DQ Rule 1: Check for Duplicates
    # If the Excel file accidentally has 'RELIANCE' listed twice, we drop the exact duplicate.
    df = df.drop_duplicates(subset=['company_id'])
    
    dupe_count = initial_count - len(df)
    if dupe_count > 0:
        print(f"⚠️ DQ ALERT: Removed {dupe_count} duplicate records.")

    # DQ Rule 2: Check for Missing/Null mandatory fields
    # A company cannot exist without an ID. If it's missing, drop that row.
    missing_count = df['company_id'].isnull().sum()
    if missing_count > 0:
        print(f"⚠️ DQ ALERT: Dropped {missing_count} records missing a company_id.")
        df = df.dropna(subset=['company_id'])

    print(f"✅ DQ Checks Passed. {len(df)} records cleared for insertion.")
    return df