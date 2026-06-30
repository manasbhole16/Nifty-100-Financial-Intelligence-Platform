import sqlite3

try:
    conn = sqlite3.connect("nifty100.db")
    cursor = conn.cursor()
    
    # Ask SQLite to list all tables that exist in this database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("🚨 WARNING: Your database is completely EMPTY! No tables exist.")
    else:
        print(f"✅ Found these tables in your database: {[t[0] for t in tables]}")
        
except Exception as e:
    print(f"Error checking database: {e}")
finally:
    conn.close()