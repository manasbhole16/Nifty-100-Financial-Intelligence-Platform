import pandas as pd
import pytest

from src.etl.normaliser import (
    normalize_ticker,
    normalize_year,
    is_valid_year_format,
    is_valid_ticker_format,
)


# ---------------------------------------------------------------------------
# normalize_ticker() -- 15 tests
# ---------------------------------------------------------------------------
class TestNormalizeTicker:
    def test_01_strips_leading_trailing_whitespace(self):
        assert normalize_ticker("  RELIANCE  ") == "RELIANCE"

    def test_02_uppercases_lowercase_input(self):
        assert normalize_ticker("reliance") == "RELIANCE"

    def test_03_mixed_case_and_whitespace(self):
        assert normalize_ticker(" TaTaMotors ") == "TATAMOTORS"

    def test_04_already_clean_ticker_unchanged(self):
        assert normalize_ticker("INFY") == "INFY"

    def test_05_single_leading_space(self):
        assert normalize_ticker(" TCS") == "TCS"

    def test_06_single_trailing_space(self):
        assert normalize_ticker("TCS ") == "TCS"

    def test_07_tab_and_newline_whitespace_stripped(self):
        assert normalize_ticker("\tTCS\n") == "TCS"

    def test_08_numeric_suffix_ticker(self):
        assert normalize_ticker("m&m") == "M&M"

    def test_09_hyphenated_ticker_uppercased(self):
        assert normalize_ticker("sbi-n") == "SBI-N"

    def test_10_passes_through_nan_untouched(self):
        assert pd.isna(normalize_ticker(float("nan")))

    def test_11_passes_through_none_untouched(self):
        assert pd.isna(normalize_ticker(None))

    def test_12_two_character_ticker(self):
        assert normalize_ticker(" M&M ") == "M&M"

    def test_13_already_uppercase_with_no_whitespace(self):
        assert normalize_ticker("HDFCBANK") == "HDFCBANK"

    def test_14_idempotent_when_applied_twice(self):
        once = normalize_ticker(" reliance ")
        twice = normalize_ticker(once)
        assert once == twice == "RELIANCE"

    def test_15_returns_string_type(self):
        assert isinstance(normalize_ticker("infy"), str)


# ---------------------------------------------------------------------------
# normalize_year() -- 20 tests
# ---------------------------------------------------------------------------
class TestNormalizeYear:
    def test_01_hyphen_two_digit_year(self):
        assert normalize_year("Mar-23") == "2023-03"

    def test_02_space_four_digit_year(self):
        assert normalize_year("Dec 2012") == "2012-12"

    def test_03_hyphen_four_digit_year(self):
        assert normalize_year("Sep-2024") == "2024-09"

    def test_04_all_twelve_months_two_digit(self):
        expected_months = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
            "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
        }
        for month_abbr, month_num in expected_months.items():
            assert normalize_year(f"{month_abbr}-20") == f"2020-{month_num}"

    def test_05_lowercase_month_abbreviation(self):
        assert normalize_year("mar-23") == "2023-03"

    def test_06_uppercase_month_abbreviation(self):
        assert normalize_year("MAR-23") == "2023-03"

    def test_07_mixed_case_month_abbreviation(self):
        assert normalize_year("mAr-23") == "2023-03"

    def test_08_two_digit_year_below_50_maps_to_2000s(self):
        assert normalize_year("Jan-05") == "2005-01"

    def test_09_four_digit_year_passthrough_month_mapping(self):
        assert normalize_year("Jan-2005") == "2005-01"

    def test_10_extra_whitespace_between_month_and_year(self):
        assert normalize_year("Dec   2012") == "2012-12"

    def test_11_unparseable_ttm_passthrough(self):
        # 'TTM' cannot be parsed into YYYY-MM; DQ-07 will flag/reject it downstream.
        assert normalize_year("TTM") == "TTM"

    def test_12_plain_four_digit_year_passthrough(self):
        assert normalize_year("2018") == "2018"

    def test_13_nan_passthrough(self):
        assert pd.isna(normalize_year(float("nan")))

    def test_14_none_passthrough(self):
        assert pd.isna(normalize_year(None))

    def test_15_already_normalised_value_unchanged(self):
        assert normalize_year("2023-03") == "2023-03"

    def test_16_empty_string_passthrough(self):
        assert normalize_year("") == ""

    def test_17_garbage_string_passthrough(self):
        assert normalize_year("not-a-year") == "not-a-year"

    def test_18_full_month_name_first_three_letters_parsed(self):
        # normalize_year() takes the first 3 letters of the month token,
        # so a full month name like 'March' still resolves correctly.
        assert normalize_year("March-2023") == "2023-03"

    def test_19_boundary_month_january(self):
        assert normalize_year("Jan-99") == "2099-01"

    def test_20_boundary_month_december(self):
        assert normalize_year("Dec-99") == "2099-12"


# ---------------------------------------------------------------------------
# Downstream validity-check helpers (used directly by DQ-07 / DQ-08)
# ---------------------------------------------------------------------------
class TestYearFormatValidity:
    def test_valid_after_normalisation(self):
        assert is_valid_year_format(normalize_year("Mar-23")) is True

    def test_invalid_plain_year(self):
        assert is_valid_year_format("2018") is False

    def test_invalid_ttm(self):
        assert is_valid_year_format("TTM") is False

    def test_nan_is_invalid(self):
        assert is_valid_year_format(float("nan")) is False


class TestTickerFormatValidity:
    def test_valid_length(self):
        assert is_valid_ticker_format("INFY") is True

    def test_too_short(self):
        assert is_valid_ticker_format("A") is False

    def test_too_long(self):
        assert is_valid_ticker_format("A" * 13) is False

    def test_boundary_lengths(self):
        assert is_valid_ticker_format("AB") is True
        assert is_valid_ticker_format("A" * 12) is True
