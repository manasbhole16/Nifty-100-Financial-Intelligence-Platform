# pyrefly: ignore [missing-import]
import pytest
import logging
from src.analytics.ratios import (
    calculate_npm, calculate_opm, calculate_roe, calculate_roce, calculate_roa,
    calculate_debt_to_equity, calculate_icr, calculate_net_debt, calculate_asset_turnover
)

# --- DAY 08: PROFITABILITY RATIOS TESTS ---

def test_npm_normal_case():
    # 1. Normal Case: 100 profit / 1000 sales = 10%
    assert calculate_npm(100, 1000) == 10.0

def test_npm_zero_denominator():
    # 2. Zero Denominator (Sales = 0) -> Should return None
    assert calculate_npm(100, 0) is None

def test_opm_normal_case():
    # 3. Normal Case OPM Calculation
    assert calculate_opm(150, 1000) == 15.0

def test_opm_cross_check_mismatch(caplog):
    # 4. OPM Mismatch > 1% (Calculated is 15%, Reported is 12%)
    with caplog.at_level(logging.WARNING):
        result = calculate_opm(150, 1000, reported_opm=12.0, company_id="TEST01")
        assert result == 15.0
        assert "OPM Mismatch [TEST01]" in caplog.text

def test_roe_normal_case():
    # 5. Normal Case ROE: 200 / (100 + 400) = 40%
    assert calculate_roe(200, 100, 400) == 40.0

def test_roe_negative_equity():
    # 6. Negative Equity (Total Equity <= 0) -> Should return None
    assert calculate_roe(200, 100, -200) is None

def test_roce_normal_case():
    # 7. Normal Case ROCE: 300 / (100 + 400 + 500) = 30%
    assert calculate_roce(300, 100, 400, 500, broad_sector="IT") == 30.0

def test_roa_zero_assets():
    # 8. Zero Assets for ROA -> Should return None
    assert calculate_roa(100, 0) is None


# --- DAY 09: LEVERAGE & EFFICIENCY RATIOS TESTS ---

def test_de_normal_case():
    ratio, flag = calculate_debt_to_equity(200, 100, 300)
    assert ratio == 0.5
    assert flag is False

def test_de_debt_free_returns_zero():
    # Borrowings = 0 should return 0, not None
    ratio, flag = calculate_debt_to_equity(0, 100, 300)
    assert ratio == 0.0

def test_de_high_leverage_flag():
    # D/E > 5 should flag True for non-financials
    ratio, flag = calculate_debt_to_equity(600, 50, 50, broad_sector="IT")
    assert ratio == 6.0
    assert flag is True

def test_de_high_leverage_financials_exception():
    # D/E > 5 should NOT flag True for Financials
    ratio, flag = calculate_debt_to_equity(600, 50, 50, broad_sector="Financials")
    assert ratio == 6.0
    assert flag is False

def test_icr_normal_case():
    icr, label, flag = calculate_icr(100, 20, 40)
    assert icr == 3.0
    assert flag is False

def test_icr_interest_zero_returns_none_and_label():
    # Interest = 0 should return None and "Debt Free" label
    icr, label, flag = calculate_icr(100, 20, 0)
    assert icr is None
    assert label == "Debt Free"

def test_icr_warning_flag():
    # ICR < 1.5 should trigger warning flag
    icr, label, flag = calculate_icr(100, 20, 100)
    assert icr == 1.2
    assert flag is True

def test_asset_turnover_zero_assets():
    # Total assets = 0 should return None
    assert calculate_asset_turnover(1000, 0) is None