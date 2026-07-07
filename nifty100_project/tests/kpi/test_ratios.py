import pytest

from src.analytics import ratios


class TestProfitabilityRatios:
    def test_net_profit_margin_normal(self):
        assert ratios.net_profit_margin(100, 1000) == pytest.approx(10.0)

    def test_net_profit_margin_zero_sales_returns_none(self):
        assert ratios.net_profit_margin(100, 0) is None

    def test_operating_profit_margin_normal(self):
        assert ratios.operating_profit_margin(200, 1000) == pytest.approx(20.0)

    def test_operating_profit_margin_zero_sales_returns_none(self):
        assert ratios.operating_profit_margin(200, 0) is None

    def test_opm_cross_check_mismatch_true(self):
        assert ratios.opm_cross_check_mismatch(20.0, 18.5) is True

    def test_opm_cross_check_mismatch_false_within_tolerance(self):
        assert ratios.opm_cross_check_mismatch(20.0, 19.5) is False

    def test_return_on_equity_normal(self):
        assert ratios.return_on_equity(150, 100, 900) == pytest.approx(15.0)

    def test_return_on_equity_zero_denominator_returns_none(self):
        assert ratios.return_on_equity(150, 0, 0) is None

    def test_return_on_equity_negative_equity_returns_none(self):
        # Day 08: "return None if equity+reserves <= 0" -- not just == 0
        assert ratios.return_on_equity(150, -500, 100) is None

    def test_roce_standard_formula(self):
        # EBIT=200, capital employed = equity+reserves+borrowings = 100+700+200=1000 -> 20%
        assert ratios.return_on_capital_employed(200, 100, 700, 200) == pytest.approx(20.0)

    def test_roce_computed_for_financial_sector_too(self):
        # Day 08: financials get a sector-relative benchmark applied downstream,
        # not a None value -- ROCE itself must still be computed.
        result = ratios.return_on_capital_employed(200, 100, 700, 200)
        assert result is not None

    def test_roce_zero_capital_employed_returns_none(self):
        assert ratios.return_on_capital_employed(200, 0, 0, 0) is None

    def test_return_on_assets_normal(self):
        assert ratios.return_on_assets(100, 1000) == pytest.approx(10.0)

    def test_return_on_assets_zero_assets_returns_none(self):
        assert ratios.return_on_assets(100, 0) is None


class TestLeverageEfficiencyRatios:
    def test_debt_to_equity_normal(self):
        assert ratios.debt_to_equity(200, 100, 900) == pytest.approx(0.2)

    def test_debt_to_equity_debt_free_returns_zero_not_none(self):
        # Day 09: "return 0 (not None) if borrowings = 0"
        assert ratios.debt_to_equity(0, 100, 900) == 0.0

    def test_debt_to_equity_zero_equity_returns_none(self):
        assert ratios.debt_to_equity(200, 0, 0) is None

    def test_high_leverage_flag_true_for_non_financial(self):
        assert ratios.high_leverage_flag(de_ratio=6.0, is_financial_sector=False) is True

    def test_high_leverage_flag_suppressed_for_financial_sector(self):
        # Day 13: high D/E flag is suppressed for Financials (structurally normal leverage)
        assert ratios.high_leverage_flag(de_ratio=6.0, is_financial_sector=True) is False

    def test_high_leverage_flag_false_below_threshold(self):
        assert ratios.high_leverage_flag(de_ratio=4.0, is_financial_sector=False) is False

    def test_interest_coverage_ratio_normal(self):
        value, label = ratios.interest_coverage_ratio(200, 20, 20)
        assert value == pytest.approx(11.0)
        assert label is None

    def test_interest_coverage_ratio_debt_free_returns_none_and_label(self):
        value, label = ratios.interest_coverage_ratio(200, 20, 0)
        assert value is None
        assert label == "Debt Free"

    def test_icr_at_risk_flag_true_below_threshold(self):
        assert ratios.icr_at_risk_flag(1.0) is True

    def test_icr_at_risk_flag_false_above_threshold(self):
        assert ratios.icr_at_risk_flag(2.0) is False

    def test_icr_at_risk_flag_false_when_none(self):
        assert ratios.icr_at_risk_flag(None) is False

    def test_net_debt_normal(self):
        assert ratios.net_debt(500, 200) == 300

    def test_net_debt_missing_borrowings_returns_none(self):
        assert ratios.net_debt(None, 200) is None

    def test_asset_turnover_normal(self):
        assert ratios.asset_turnover(1000, 1300) == pytest.approx(1000 / 1300)

    def test_asset_turnover_zero_assets_returns_none(self):
        assert ratios.asset_turnover(1000, 0) is None
