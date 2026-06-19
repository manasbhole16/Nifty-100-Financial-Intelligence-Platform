# pyrefly: ignore [missing-import]
import pytest
from src.etl.loader import normalize_ticker, normalize_year

def test_normalize_ticker():
    assert normalize_ticker(" tcs ") == "TCS"
    assert normalize_ticker("infy") == "INFY"
    assert normalize_ticker("RELIANCE") == "RELIANCE"
    assert normalize_ticker(" HDFC BANK ") == "HDFC BANK"
    assert normalize_ticker(None) is None

def test_normalize_year():
    assert normalize_year("Mar-23") == "2023-03"
    assert normalize_year("Dec-24") == "2024-12"
    assert normalize_year(" Mar-08 ") == "2008-03" # with spaces
    assert normalize_year("Jan-15") == "2015-01"
    assert normalize_year(None) is None
    assert normalize_year("Invalid-Date") == "Invalid-Date" # Should not crash