# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
import pandas as pd
import os

router = APIRouter(prefix="/api/v1/companies", tags=["Companies Module"])

DB_PATH = "data/nifty100.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@router.get("/", response_model=list)
def list_companies(db: sqlite3.Connection = Depends(get_db)):
    """Listing of all registered companies."""
    cursor = db.cursor()
    rows = cursor.execute("SELECT company_id, company_name FROM companies").fetchall()
    return [dict(row) for row in rows]

@router.get("/{company_id}", response_model=dict)
def get_company_profile(company_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Fetches profile, sector, and assigned ML cluster."""
    cursor = db.cursor()
    # Join with sectors table based on your schema
    company_row = cursor.execute("""
        SELECT c.*, s.broad_sector, s.sub_sector 
        FROM companies c
        LEFT JOIN sectors s ON c.company_id = s.company_id
        WHERE c.company_id = ?
    """, (company_id,)).fetchone()
    
    if not company_row:
        raise HTTPException(status_code=404, detail="Company not found.")
    
    res = dict(company_row)
    
    # Attach ML cluster label
    try:
        df_labels = pd.read_csv("output/cluster_labels.csv")
        lbl_match = df_labels[df_labels['company_id'] == company_id]
        if not lbl_match.empty:
            res['cluster_id'] = int(lbl_match.iloc[0]['cluster_id'])
            res['cluster_name'] = str(lbl_match.iloc[0]['cluster_name'])
    except Exception:
        res['cluster_id'] = None
        
    return res