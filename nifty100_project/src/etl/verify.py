import pandas as pd
from src.etl.database import engine

def verify_database():
    print("🔍 Querying the SQLite database...")
    
    # Write a SQL query to fetch the first 5 rows
    query = "SELECT * FROM companies LIMIT 5;"
    
    # Use pandas to run the query and format the output
    df = pd.read_sql(query, engine)
    
    print("\n✅ Top 5 Companies in the Database:")
    print("-" * 50)
    print(df.to_string(index=False))
    print("-" * 50)

if __name__ == "__main__":
    verify_database()