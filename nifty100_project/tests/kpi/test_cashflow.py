# pyrefly: ignore [missing-import]
import pytest
from src.analytics.cashflow_kpis import (
    calculate_fcf, calculate_cfo_quality_score, 
    calculate_capex_intensity, classify_capital_allocation
)

def test_fcf_normal_case():
    # CFO of 500, CapEx of 200 -> FCF should be 300
    assert calculate_fcf(500, 200) == 300

def test_cfo_quality_normal():
    # CFO of 150, PAT of 100 -> Score of 1.5
    assert calculate_cfo_quality_score(150, 100) == 1.5

def test_cfo_quality_zero_pat():
    # Zero PAT should return None to avoid division by zero
    assert calculate_cfo_quality_score(150, 0) is None

def test_capex_intensity_normal():
    # CapEx of 50, Revenue of 1000 -> 5.0%
    assert calculate_capex_intensity(50, 1000) == 5.0

def test_capex_intensity_zero_revenue():
    assert calculate_capex_intensity(50, 0) is None

def test_classifier_mature_reinvestor():
    # + CFO (1000), - CFI (-500), - CFF (-200)
    result = classify_capital_allocation(1000, -500, -200)
    assert result == "Mature Reinvestor / Shareholder Returns"

def test_classifier_high_growth_burn():
    # - CFO (-100), - CFI (-500), + CFF (800)
    result = classify_capital_allocation(-100, -500, 800)
    assert result == "High-Growth Burn / Start-up"

def test_classifier_severe_distress():
    # - CFO (-100), - CFI (-500), - CFF (-800)
    result = classify_capital_allocation(-100, -50, -20)
    assert result == "Severe Distress (Cash Burn)"