import pandas as pd
import pytest

from src.etl.validator import run_validations


def _base_dataframes():
    """Minimal, internally-consistent dataset covering all 12 files."""
    companies = pd.DataFrame({
        "id": ["AAA", "BBB"],
        "company_logo": [None, None],
        "company_name": ["Alpha Ltd", "Beta Ltd"],
        "chart_link": [None, None],
        "about_company": [None, None],
        "website": [None, None],
        "nse_profile": [None, None],
        "bse_profile": [None, None],
        "face_value": [10.0, 10.0],
        "book_value": [100.0, 200.0],
        "roce_percentage": [15.0, 20.0],
        "roe_percentage": [12.0, 18.0],
    })

    pl = pd.DataFrame({
        "id": [1, 2],
        "company_id": ["AAA", "BBB"],
        "year": ["2023-03", "2023-03"],
        "sales": [1000.0, 2000.0],
        "expenses": [800.0, 1500.0],
        "operating_profit": [200.0, 500.0],
        "opm_percentage": [20.0, 25.0],
        "other_income": [10.0, 10.0],
        "interest": [5.0, 5.0],
        "depreciation": [20.0, 20.0],
        "profit_before_tax": [185.0, 485.0],
        "tax_percentage": [25.0, 25.0],
        "net_profit": [138.75, 363.75],
        "eps": [5.0, 10.0],
        "dividend_payout": [30.0, 40.0],
    })

    bs = pd.DataFrame({
        "id": [1, 2],
        "company_id": ["AAA", "BBB"],
        "year": ["2023-03", "2023-03"],
        "equity_capital": [100.0, 100.0],
        "reserves": [900.0, 900.0],
        "borrowings": [200.0, 200.0],
        "other_liabilities": [100.0, 100.0],
        "total_liabilities": [1300.0, 1300.0],
        "fixed_assets": [800.0, 800.0],
        "cwip": [50.0, 50.0],
        "investments": [200.0, 200.0],
        "other_asset": [250.0, 250.0],
        "total_assets": [1300.0, 1300.0],
    })

    cf = pd.DataFrame({
        "id": [1, 2],
        "company_id": ["AAA", "BBB"],
        "year": ["2023-03", "2023-03"],
        "operating_activity": [100.0, 200.0],
        "investing_activity": [-30.0, -50.0],
        "financing_activity": [-20.0, -30.0],
        "net_cash_flow": [50.0, 120.0],
    })

    analysis = pd.DataFrame({
        "id": [1], "company_id": ["AAA"],
        "compounded_sales_growth": ["10 Years: 12%"],
        "compounded_profit_growth": ["10 Years: 15%"],
        "stock_price_cagr": ["10 Years: 18%"],
        "roe": ["10 Years: 14%"],
    })

    docs = pd.DataFrame({
        "id": [1, 2], "company_id": ["AAA", "BBB"],
        "Year": [2023, 2023],
        "Annual_Report": ["http://example.com/a.pdf", "http://example.com/b.pdf"],
    })

    proscons = pd.DataFrame({
        "id": [1], "company_id": ["AAA"], "pros": ["Strong brand"], "cons": ["High debt"],
    })

    sectors = pd.DataFrame({
        "id": [1, 2], "company_id": ["AAA", "BBB"],
        "broad_sector": ["Industrials", "Financials"],
        "sub_sector": ["Cement", "Banks"],
        "index_weight_pct": [1.2, 2.5],
        "market_cap_category": ["Large Cap", "Large Cap"],
    })

    market_cap = pd.DataFrame({
        "id": [1, 2], "company_id": ["AAA", "BBB"], "year": [2023, 2023],
        "market_cap_crore": [50000.0, 90000.0],
        "enterprise_value_crore": [55000.0, 95000.0],
        "pe_ratio": [22.0, 15.0], "pb_ratio": [3.0, 2.0],
        "ev_ebitda": [12.0, 10.0], "dividend_yield_pct": [1.0, 1.5],
    })

    stock_prices = pd.DataFrame({
        "id": [1, 2], "company_id": ["AAA", "BBB"], "date": ["2023-03-31", "2023-03-31"],
        "open_price": [100.0, 200.0], "high_price": [105.0, 205.0],
        "low_price": [98.0, 198.0], "close_price": [102.0, 202.0],
        "volume": [1000, 2000], "adjusted_close": [102.0, 202.0],
    })

    peer_groups = pd.DataFrame({
        "id": [1], "peer_group_name": ["Cement Peers"], "company_id": ["AAA"], "is_benchmark": [True],
    })

    fr_ref = pd.DataFrame({
        "id": [1], "company_id": ["AAA"], "year": ["2023-03"],
        "net_profit_margin_pct": [13.9], "operating_profit_margin_pct": [20.0],
        "return_on_equity_pct": [12.0], "debt_to_equity": [0.2],
        "interest_coverage": [40.0], "asset_turnover": [0.8],
        "free_cash_flow_cr": [70.0], "capex_cr": [30.0],
        "earnings_per_share": [5.0], "book_value_per_share": [100.0],
        "dividend_payout_ratio_pct": [30.0], "total_debt_cr": [200.0],
        "cash_from_operations_cr": [100.0],
    })

    return {
        "companies.xlsx": companies, "profitandloss.xlsx": pl, "balancesheet.xlsx": bs,
        "cashflow.xlsx": cf, "analysis.xlsx": analysis, "documents.xlsx": docs,
        "prosandcons.xlsx": proscons, "sectors.xlsx": sectors, "market_cap.xlsx": market_cap,
        "stock_prices.xlsx": stock_prices, "peer_groups.xlsx": peer_groups,
        "financial_ratios.xlsx": fr_ref,
    }


def test_clean_dataset_produces_no_critical_failures():
    dfs = _base_dataframes()
    cleaned, failures = run_validations(dfs)
    assert (failures["severity"] == "CRITICAL").sum() == 0
    assert len(cleaned["companies.xlsx"]) == 2


def test_dq01_duplicate_company_id_flagged_and_deduped():
    dfs = _base_dataframes()
    dfs["companies.xlsx"] = pd.concat([dfs["companies.xlsx"], dfs["companies.xlsx"].iloc[[0]]], ignore_index=True)
    cleaned, failures = run_validations(dfs)
    assert "DQ-01" in failures["rule_id"].values
    assert len(cleaned["companies.xlsx"]) == 2  # deduped back to 2 unique


def test_dq02_duplicate_annual_pk_deduped():
    dfs = _base_dataframes()
    dup_row = dfs["profitandloss.xlsx"].iloc[[0]].copy()
    dup_row["sales"] = 9999.0
    dfs["profitandloss.xlsx"] = pd.concat([dfs["profitandloss.xlsx"], dup_row], ignore_index=True)
    cleaned, failures = run_validations(dfs)
    assert "DQ-02" in failures["rule_id"].values
    pl_out = cleaned["profitandloss.xlsx"]
    assert pl_out[pl_out["company_id"] == "AAA"].shape[0] == 1
    assert pl_out[pl_out["company_id"] == "AAA"]["sales"].iloc[0] == 9999.0  # keeps last


def test_dq03_orphan_fk_rejected():
    dfs = _base_dataframes()
    orphan = dfs["profitandloss.xlsx"].iloc[[0]].copy()
    orphan["company_id"] = "ZZZ"
    dfs["profitandloss.xlsx"] = pd.concat([dfs["profitandloss.xlsx"], orphan], ignore_index=True)
    cleaned, failures = run_validations(dfs)
    assert "DQ-03" in failures["rule_id"].values
    assert "ZZZ" not in cleaned["profitandloss.xlsx"]["company_id"].values


def test_dq04_balance_sheet_imbalance_flagged_not_rejected():
    dfs = _base_dataframes()
    dfs["balancesheet.xlsx"].loc[0, "total_assets"] = 2000.0  # now off from liabilities
    cleaned, failures = run_validations(dfs)
    assert "DQ-04" in failures["rule_id"].values
    assert len(cleaned["balancesheet.xlsx"]) == 2  # not rejected, just flagged


def test_dq07_bad_year_format_rejected():
    dfs = _base_dataframes()
    dfs["profitandloss.xlsx"].loc[0, "year"] = "TTM"
    cleaned, failures = run_validations(dfs)
    assert "DQ-07" in failures["rule_id"].values
    assert len(cleaned["profitandloss.xlsx"]) == 1


def test_dq08_bad_ticker_length_rejected():
    dfs = _base_dataframes()
    dfs["profitandloss.xlsx"].loc[0, "company_id"] = "A"
    cleaned, failures = run_validations(dfs)
    assert "DQ-08" in failures["rule_id"].values
    assert "A" not in cleaned["profitandloss.xlsx"]["company_id"].values


def test_dq09_net_cash_mismatch_recomputed():
    dfs = _base_dataframes()
    dfs["cashflow.xlsx"].loc[0, "net_cash_flow"] = 99999.0
    cleaned, failures = run_validations(dfs)
    assert "DQ-09" in failures["rule_id"].values
    fixed_val = cleaned["cashflow.xlsx"].loc[cleaned["cashflow.xlsx"]["company_id"] == "AAA", "net_cash_flow"].iloc[0]
    assert fixed_val == 50.0  # recomputed from components


def test_dq10_negative_fixed_assets_coerced_to_zero():
    dfs = _base_dataframes()
    dfs["balancesheet.xlsx"].loc[0, "fixed_assets"] = -50.0
    cleaned, failures = run_validations(dfs)
    assert "DQ-10" in failures["rule_id"].values
    assert cleaned["balancesheet.xlsx"].loc[0, "fixed_assets"] == 0


def test_dq11_tax_rate_out_of_range_flagged():
    dfs = _base_dataframes()
    dfs["profitandloss.xlsx"].loc[0, "tax_percentage"] = 95.0
    _, failures = run_validations(dfs)
    assert "DQ-11" in failures["rule_id"].values


def test_dq12_dividend_payout_over_cap_flagged():
    dfs = _base_dataframes()
    dfs["profitandloss.xlsx"].loc[0, "dividend_payout"] = 250.0
    _, failures = run_validations(dfs)
    assert "DQ-12" in failures["rule_id"].values


def test_dq14_eps_sign_inconsistency_flagged():
    dfs = _base_dataframes()
    dfs["profitandloss.xlsx"].loc[0, "eps"] = -1.0  # net_profit is positive
    _, failures = run_validations(dfs)
    assert "DQ-14" in failures["rule_id"].values


def test_dq16_low_coverage_flagged():
    # Only one year of history for both companies -> should be flagged (< 5 years)
    dfs = _base_dataframes()
    _, failures = run_validations(dfs)
    assert "DQ-16" in failures["rule_id"].values
