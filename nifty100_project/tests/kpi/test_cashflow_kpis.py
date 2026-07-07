import pytest

from src.analytics import cashflow_kpis as cfk


class TestFreeCashFlow:
    def test_normal(self):
        assert cfk.free_cash_flow(100, -30) == 70

    def test_negative_fcf_allowed(self):
        assert cfk.free_cash_flow(50, -80) == -30

    def test_missing_value_returns_none(self):
        assert cfk.free_cash_flow(None, -30) is None


class TestCfoQualityScore:
    def test_high_quality(self):
        score, label = cfk.cfo_quality_score([1.2, 1.3, 1.1])
        assert score > 1.0
        assert label == "High Quality"

    def test_moderate(self):
        score, label = cfk.cfo_quality_score([0.6, 0.7])
        assert 0.5 <= score <= 1.0
        assert label == "Moderate"

    def test_accrual_risk(self):
        score, label = cfk.cfo_quality_score([0.2, 0.3])
        assert score < 0.5
        assert label == "Accrual Risk"

    def test_no_valid_years_returns_none(self):
        assert cfk.cfo_quality_score([]) == (None, None)


class TestSingleYearCfoPatRatio:
    def test_normal(self):
        assert cfk.single_year_cfo_pat_ratio(100, 50) == pytest.approx(2.0)

    def test_negative_pat_returns_none(self):
        assert cfk.single_year_cfo_pat_ratio(100, -10) is None

    def test_zero_pat_returns_none(self):
        assert cfk.single_year_cfo_pat_ratio(100, 0) is None


class TestCapexIntensity:
    def test_asset_light_label(self):
        value, label = cfk.capex_intensity(-20, 1000)
        assert value == pytest.approx(2.0)
        assert label == "Asset Light"

    def test_moderate_label(self):
        value, label = cfk.capex_intensity(-50, 1000)
        assert value == pytest.approx(5.0)
        assert label == "Moderate"

    def test_capital_intensive_label(self):
        value, label = cfk.capex_intensity(-100, 1000)
        assert value == pytest.approx(10.0)
        assert label == "Capital Intensive"

    def test_zero_sales_returns_none(self):
        assert cfk.capex_intensity(-50, 0) == (None, None)


class TestFcfConversionRate:
    def test_normal(self):
        assert cfk.fcf_conversion_rate(70, 50) == pytest.approx(140.0)

    def test_zero_operating_profit_returns_none(self):
        assert cfk.fcf_conversion_rate(70, 0) is None


class TestCapitalAllocationClassifier:
    def test_reinvestor(self):
        assert cfk.classify_capital_allocation(100, -50, -20, cfo_pat_quality_score=0.8) == "Reinvestor"

    def test_shareholder_returns_high_quality_tiebreak(self):
        assert cfk.classify_capital_allocation(100, -50, -20, cfo_pat_quality_score=1.5) == "Shareholder Returns"

    def test_liquidating_assets(self):
        assert cfk.classify_capital_allocation(100, 50, -20) == "Liquidating Assets"

    def test_distress_signal(self):
        assert cfk.classify_capital_allocation(-100, 50, 20) == "Distress Signal"

    def test_growth_funded_by_debt(self):
        assert cfk.classify_capital_allocation(-100, -50, 20) == "Growth Funded by Debt"

    def test_cash_accumulator(self):
        assert cfk.classify_capital_allocation(100, 50, 20) == "Cash Accumulator"

    def test_pre_revenue(self):
        assert cfk.classify_capital_allocation(-100, -50, -20) == "Pre-Revenue"

    def test_mixed_plus_minus_plus(self):
        assert cfk.classify_capital_allocation(100, -50, 20) == "Mixed"

    def test_unlisted_combo_falls_back_to_mixed(self):
        # (-,+,-) is not one of the 8 explicitly enumerated sign tuples
        assert cfk.classify_capital_allocation(-100, 50, -20) == "Mixed"

    def test_missing_data_falls_back_to_mixed(self):
        assert cfk.classify_capital_allocation(None, None, None) == "Mixed"

    def test_all_patterns_in_documented_list(self):
        assert cfk.classify_capital_allocation(100, -50, -20) in cfk.CAPITAL_ALLOCATION_PATTERNS
