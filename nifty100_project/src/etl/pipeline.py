import pandas as pd
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError
from src.etl.database import SessionLocal
from src.etl.models import Company
from src.etl.loader import normalize_ticker

def run_company_pipeline():
    print("🚀 Starting ETL Pipeline for Companies...")
    db = SessionLocal()
    
    try:
        file_path = "data/raw/companies.xlsx"
        print(f"📂 Reading data from {file_path}...")
        
        # Read the file
        df = pd.read_excel(file_path, header=1)
        
        # 1. Rename 'id' to 'company_id' (company_name is already correct!)
        df = df.rename(columns={'id': 'company_id'})
        
        # 2. Add 'sector' and 'industry' as blank/default since they are missing from the Excel file
        df['sector'] = "Not Provided"
        df['industry'] = "Not Provided"
        
        # 3. Clean the tickers using our Day 2 logic
        df['company_id'] = df['company_id'].apply(normalize_ticker)
        df = df.dropna(subset=['company_id'])

        records_inserted = 0

        print("⏳ Inserting records into the database...")
        for _, row in df.iterrows():
            new_company = Company(
                company_id=row['company_id'],
                company_name=row['company_name'],
                sector=row['sector'],
                industry=row['industry']
            )
            
            db.add(new_company)
            records_inserted += 1
            
        db.commit()
        print(f"✅ SUCCESS! {records_inserted} companies successfully inserted into the database.")

    except IntegrityError:
        db.rollback()
        print("⚠️ Warning: Data already exists in the database.")
    except Exception as e:
        db.rollback()
        print(f"❌ CRITICAL ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_company_pipeline()