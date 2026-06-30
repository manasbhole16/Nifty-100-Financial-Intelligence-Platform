import sqlite3
import pandas as pd

# Connect to your newly populated database
conn = sqlite3.connect("nifty100_project/data/nifty100.db")

# Load the table
df = pd.read_sql_query("SELECT * FROM financial_ratios", conn)

print(f"Total rows in database: {len(df)}\n")

# This will print out the count of missing (NULL) values for every single column
print("--- Missing (NULL) Value Count per Column ---")
print(df.isnull().sum())

conn.close()