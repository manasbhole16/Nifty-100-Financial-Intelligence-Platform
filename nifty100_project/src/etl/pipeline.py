import pandas as pd
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import IntegrityError
from src.etl.database import SessionLocal
from src.etl.models import Company
from src.etl.loader import normalize_ticker
from src.etl.validation import validate_company_data
# NEW DAY 6 IMPORT: Bring in our custom logger
from src.etl.logger import get_logger

# Initialize the logger for this specific file
logger = get_logger(__name__)

def run_company_pipeline():
    logger.info("Starting ETL Pipeline for Companies...")
    db = SessionLocal()
    
    try:
        file_path = "data/raw/companies.xlsx"
        logger.info(f"Reading data from {file_path}...")
        
        df = pd.read_excel(file_path, header=1)
        
        df = df.rename(columns={'id': 'company_id'})
        df['sector'] = "Not Provided"
        df['industry'] = "Not Provided"
        
        df['company_id'] = df['company_id'].apply(normalize_ticker)
        
        # Pass through Day 5 DQ Bouncer
        logger.info("Executing Data Quality validations...")
        df = validate_company_data(df)

        records_inserted = 0

        logger.info("Inserting verified records into the database...")
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
        logger.info(f"SUCCESS: {records_inserted} companies safely inserted into the database.")

    except IntegrityError:
        db.rollback()
        logger.warning("Data already exists in the database. Insertion skipped to prevent duplicates.")
    except Exception as e:
        db.rollback()
        logger.error(f"CRITICAL PIPELINE FAILURE: {e}")
    finally:
        db.close()
        logger.info("Database connection securely closed.")

if __name__ == "__main__":
    run_company_pipeline()