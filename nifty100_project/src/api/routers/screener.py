# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
import sqlite3

router = APIRouter(prefix="/api/v1/screener", tags=["Investment Screener Module"])
DB_PATH = "data/nifty100.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@router.get("/filter")
def execute_screen(min_roe: float = 0.0, max_de: float = 999.0, db: sqlite3.Connection = Depends(get_db)):
    """Filters companies based on ROE and Debt-to-Equity thresholds."""
    cursor = db.cursor()
    query = """
        SELECT f.company_id, f.return_on_equity_pct, f.debt_to_equity
        FROM financial_ratios f
        WHERE f.year = (SELECT MAX(year) FROM financial_ratios)
          AND f.return_on_equity_pct >= ?
          AND f.debt_to_equity <= ?
    """
    rows = cursor.execute(query, (min_roe, max_de)).fetchall()
    return {"results": [dict(row) for row in rows]}