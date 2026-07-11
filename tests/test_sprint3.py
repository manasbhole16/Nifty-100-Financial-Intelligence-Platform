import os
import sqlite3
import pandas as pd

def test_screener_output_exists():
    """Verify Day 17 generated the screener Excel file."""
    assert os.path.exists('output/screener_output.xlsx'), "Screener output missing!"

def test_peer_comparison_exists_and_has_11_sheets():
    """Verify Day 19 generated the peer Excel file with exactly 11 sector sheets."""
    file_path = 'output/peer_comparison.xlsx'
    assert os.path.exists(file_path), "Peer comparison missing!"
    
    # Read the Excel file and count the tabs
    xl = pd.ExcelFile(file_path)
    sheet_count = len(xl.sheet_names)
    assert sheet_count == 11, f"Expected 11 peer group sheets, but found {sheet_count}."

def test_radar_charts_generated():
    """Verify Day 20 successfully saved PNG images."""
    folder_path = 'reports/radar_charts'
    assert os.path.exists(folder_path), "Radar charts folder missing!"
    
    charts = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    assert len(charts) > 0, "No radar charts were actually saved!"

def test_peer_percentiles_saved_to_db():
    """Verify Day 18 successfully injected calculations into SQLite."""
    conn = sqlite3.connect('data/nifty100.db')
    cursor = conn.cursor()
    
    # Check if table exists and has rows
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='peer_percentiles'")
    assert cursor.fetchone() is not None, "peer_percentiles table does not exist!"
    
    cursor.execute("SELECT count(*) FROM peer_percentiles")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count > 0, "peer_percentiles table is completely empty!"
