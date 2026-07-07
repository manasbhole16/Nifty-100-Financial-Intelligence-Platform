import pytest

from src.analytics.cagr import (
    compute_cagr, cagr_for_window, compute_all_cagr_windows,
    FLAG_DECLINE_TO_LOSS, FLAG_TURNAROUND, FLAG_BOTH_NEGATIVE, FLAG_ZERO_BASE, FLAG_INSUFFICIENT,
)


class TestComputeCagr:
    def test_positive_to_positive_normal_growth(self):
        cagr, flag = compute_cagr(100, 200, 3)
        assert flag is None
        assert cagr == pytest.approx(((200 / 100) ** (1 / 3) - 1) * 100)

    def test_positive_to_positive_normal_decline(self):
        cagr, flag = compute_cagr(200, 100, 5)
        assert flag is None
        assert cagr < 0

    def test_missing_begin_value_insufficient(self):
        assert compute_cagr(None, 200, 3) == (None, FLAG_INSUFFICIENT)

    def test_missing_end_value_insufficient(self):
        assert compute_cagr(100, None, 3) == (None, FLAG_INSUFFICIENT)

    def test_zero_num_years_insufficient(self):
        assert compute_cagr(100, 200, 0) == (None, FLAG_INSUFFICIENT)

    def test_zero_base_flag(self):
        assert compute_cagr(0, 200, 3) == (None, FLAG_ZERO_BASE)

    def test_positive_to_negative_decline_to_loss(self):
        cagr, flag = compute_cagr(50, -10, 3)
        assert cagr is None
        assert flag == FLAG_DECLINE_TO_LOSS

    def test_negative_to_positive_turnaround(self):
        cagr, flag = compute_cagr(-50, 100, 3)
        assert cagr is None
        assert flag == FLAG_TURNAROUND

    def test_negative_to_negative_both_negative(self):
        cagr, flag = compute_cagr(-50, -10, 3)
        assert cagr is None
        assert flag == FLAG_BOTH_NEGATIVE

    def test_negative_to_zero_both_negative_bucket(self):
        cagr, flag = compute_cagr(-50, 0, 3)
        assert cagr is None
        assert flag == FLAG_BOTH_NEGATIVE


class TestCagrForWindow:
    def test_insufficient_history(self):
        years = ["2020-03", "2021-03"]
        values = {"2020-03": 100, "2021-03": 110}
        cagr, flag = cagr_for_window(years, values, "2021-03", 3)
        assert cagr is None
        assert flag == FLAG_INSUFFICIENT

    def test_exact_window_available(self):
        years = ["2018-03", "2019-03", "2020-03", "2021-03"]
        values = {"2018-03": 100, "2019-03": 110, "2020-03": 120, "2021-03": 133.1}
        cagr, flag = cagr_for_window(years, values, "2021-03", 3)
        assert flag is None
        assert cagr == pytest.approx(10.0, abs=0.1)

    def test_latest_year_not_present(self):
        years = ["2018-03", "2019-03"]
        values = {"2018-03": 100, "2019-03": 110}
        cagr, flag = cagr_for_window(years, values, "2025-03", 3)
        assert cagr is None
        assert flag == FLAG_INSUFFICIENT


class TestComputeAllCagrWindows:
    def test_returns_value_and_flag_columns_for_all_windows(self):
        years = [f"{y}-03" for y in range(2011, 2022)]  # 11 years
        values = {f"{y}-03": 100 * (1.1 ** (y - 2011)) for y in range(2011, 2022)}
        result = compute_all_cagr_windows(years, values, "2021-03")
        expected_keys = {
            "cagr_3yr", "cagr_3yr_flag", "cagr_5yr", "cagr_5yr_flag", "cagr_10yr", "cagr_10yr_flag",
        }
        assert set(result.keys()) == expected_keys
        assert result["cagr_10yr"] == pytest.approx(10.0, abs=0.5)
        assert result["cagr_10yr_flag"] is None

    def test_turnaround_flag_surfaces_on_the_right_window(self):
        years = ["2019-03", "2020-03", "2021-03", "2022-03"]
        values = {"2019-03": -50.0, "2020-03": -20.0, "2021-03": 10.0, "2022-03": 40.0}
        result = compute_all_cagr_windows(years, values, "2022-03")
        assert result["cagr_3yr_flag"] == FLAG_TURNAROUND
        assert result["cagr_3yr"] is None
