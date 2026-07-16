"""
Data Quality validator — implements all 16 DQ rules from Section 14 of the
project specification (DQ-01 .. DQ-16). Day 03 / D-03 deliverable.

run_validations() takes the dict of raw DataFrames produced by
src.etl.loader.load_all_data() and returns:
    (cleaned_dataframes, validation_failures_df)

Each row logged into validation_failures_df carries:
    rule_id, table, company_id, year, field, issue, severity

CRITICAL rows cause the offending record to be rejected or the row
corrected per the rule's documented Action. WARNING/INFO rows are
flagged but the record is kept (per spec: "Flag row. Do not reject.").
"""

import os
import pandas as pd
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from src.etl.normaliser import is_valid_year_format, is_valid_ticker_format
from src.etl.logger import get_logger

logger = get_logger(__name__)

load_dotenv()  # reads .env at project root if present (see config/.env.template)

# Whether to perform live HTTP HEAD checks for DQ-13 (annual report URLs).
# Default False: the sandbox / CI network is typically restricted, and
# validating ~1,585 external URLs on every run is slow and non-deterministic.
# Set VALIDATE_DOCUMENT_URLS=true in .env to enable live checks.
VALIDATE_URLS = os.getenv("VALIDATE_DOCUMENT_URLS", "false").lower() == "true"


def _flag(failures, rule_id, table, company_id, year, field, issue, severity):
    failures.append({
        "rule_id": rule_id,
        "table": table,
        "company_id": company_id,
        "year": year,
        "field": field,
        "issue": issue,
        "severity": severity,
    })


# --------------------------------------------------------------------------
# DQ-01 Company PK Uniqueness (CRITICAL)
# --------------------------------------------------------------------------
def _dq01_company_pk_uniqueness(companies: pd.DataFrame, failures: list) -> pd.DataFrame:
    dup_mask = companies["id"].duplicated(keep=False)
    if dup_mask.any():
        for ticker in companies.loc[dup_mask, "id"].unique():
            _flag(failures, "DQ-01", "companies", ticker, None, "id",
                  "Duplicate company ticker (PK violation)", "CRITICAL")
        logger.error(f"DQ-01 CRITICAL: {dup_mask.sum()} duplicate company id rows found.")
    return companies.drop_duplicates(subset=["id"], keep="last")


# --------------------------------------------------------------------------
# DQ-02 Annual PK Uniqueness (CRITICAL) — dedupe (company_id, year), keep last
# --------------------------------------------------------------------------
def _dq02_annual_pk_uniqueness(df: pd.DataFrame, table_name: str, failures: list) -> pd.DataFrame:
    dup_mask = df.duplicated(subset=["company_id", "year"], keep=False)
    if dup_mask.any():
        for _, row in df.loc[dup_mask].iterrows():
            _flag(failures, "DQ-02", table_name, row["company_id"], row["year"],
                  "company_id+year", "Duplicate (company_id, year) pair", "CRITICAL")
        logger.warning(f"DQ-02 CRITICAL: {dup_mask.sum()} duplicate rows in {table_name}. Deduplicating (keep last).")
    return df.drop_duplicates(subset=["company_id", "year"], keep="last")


# --------------------------------------------------------------------------
# DQ-03 FK Integrity (CRITICAL) — reject orphan rows
# --------------------------------------------------------------------------
def _dq03_fk_integrity(df: pd.DataFrame, table_name: str, valid_ids: set, failures: list) -> pd.DataFrame:
    orphan_mask = ~df["company_id"].isin(valid_ids)
    if orphan_mask.any():
        for _, row in df.loc[orphan_mask].iterrows():
            year_val = row["year"] if "year" in df.columns else None
            _flag(failures, "DQ-03", table_name, row["company_id"], year_val,
                  "company_id", "Orphan row: company_id not found in companies.id", "CRITICAL")
        logger.warning(f"DQ-03 CRITICAL: {orphan_mask.sum()} orphan rows rejected from {table_name}.")
    return df.loc[~orphan_mask].copy()


# --------------------------------------------------------------------------
# DQ-04 Balance Sheet Balance (WARNING) — flag only, do not reject
# --------------------------------------------------------------------------
def _dq04_balance_sheet_balance(bs: pd.DataFrame, failures: list) -> pd.Series:
    ratio = (bs["total_assets"] - bs["total_liabilities"]).abs() / bs["total_assets"].replace(0, pd.NA)
    ratio = ratio.replace([float("inf"), float("-inf")], pd.NA)
    flagged = ratio.fillna(0) >= 0.01
    for idx in bs.index[flagged]:
        row = bs.loc[idx]
        _flag(failures, "DQ-04", "balancesheet", row["company_id"], row["year"],
              "total_assets/total_liabilities",
              f"Balance sheet imbalance: assets={row['total_assets']}, liabilities={row['total_liabilities']}",
              "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-05 OPM Cross-Check (WARNING)
# --------------------------------------------------------------------------
def _dq05_opm_cross_check(pl: pd.DataFrame, failures: list) -> pd.Series:
    computed_opm = (pl["operating_profit"] / pl["sales"].replace(0, pd.NA)) * 100
    diff = (pl["opm_percentage"] - computed_opm).abs()
    flagged = diff.fillna(0) >= 1.0
    for idx in pl.index[flagged]:
        row = pl.loc[idx]
        _flag(failures, "DQ-05", "profitandloss", row["company_id"], row["year"],
              "opm_percentage",
              f"OPM mismatch: source={row['opm_percentage']}, computed={computed_opm.loc[idx]:.2f}",
              "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-06 Positive Sales (WARNING) — non-bank companies only
# --------------------------------------------------------------------------
def _dq06_positive_sales(pl: pd.DataFrame, financial_tickers: set, failures: list) -> pd.Series:
    is_non_bank = ~pl["company_id"].isin(financial_tickers)
    flagged = is_non_bank & (pl["sales"].fillna(0) <= 0)
    for idx in pl.index[flagged]:
        row = pl.loc[idx]
        _flag(failures, "DQ-06", "profitandloss", row["company_id"], row["year"],
              "sales", f"Non-positive sales for non-financial company: {row['sales']}", "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-07 Year Format (CRITICAL) — reject unparseable rows
# --------------------------------------------------------------------------
def _dq07_year_format(df: pd.DataFrame, table_name: str, failures: list) -> pd.DataFrame:
    valid_mask = df["year"].apply(is_valid_year_format)
    if (~valid_mask).any():
        for _, row in df.loc[~valid_mask].iterrows():
            _flag(failures, "DQ-07", table_name, row["company_id"], row["year"],
                  "year", f"Unparseable year value after normalisation: '{row['year']}'", "CRITICAL")
        logger.warning(f"DQ-07 CRITICAL: {(~valid_mask).sum()} rows with bad year format rejected from {table_name}.")
    return df.loc[valid_mask].copy()


# --------------------------------------------------------------------------
# DQ-08 Ticker Format (CRITICAL) — reject out-of-range length
# --------------------------------------------------------------------------
def _dq08_ticker_format(df: pd.DataFrame, table_name: str, ticker_col: str, failures: list) -> pd.DataFrame:
    valid_mask = df[ticker_col].apply(is_valid_ticker_format)
    if (~valid_mask).any():
        for _, row in df.loc[~valid_mask].iterrows():
            _flag(failures, "DQ-08", table_name, row[ticker_col], None,
                  ticker_col, f"Ticker length out of 2-12 char range: '{row[ticker_col]}'", "CRITICAL")
        logger.warning(f"DQ-08 CRITICAL: {(~valid_mask).sum()} rows with bad ticker format rejected from {table_name}.")
    return df.loc[valid_mask].copy()


# --------------------------------------------------------------------------
# DQ-09 Net Cash Check (WARNING) — recompute net_cash_flow if mismatch
# --------------------------------------------------------------------------
def _dq09_net_cash_check(cf: pd.DataFrame, failures: list) -> pd.DataFrame:
    cf = cf.copy()
    computed = cf["operating_activity"].fillna(0) + cf["investing_activity"].fillna(0) + cf["financing_activity"].fillna(0)
    diff = (cf["net_cash_flow"] - computed).abs()
    mismatch = diff.fillna(0) > 10
    for idx in cf.index[mismatch]:
        row = cf.loc[idx]
        _flag(failures, "DQ-09", "cashflow", row["company_id"], row["year"],
              "net_cash_flow",
              f"Net cash flow mismatch: reported={row['net_cash_flow']}, computed={computed.loc[idx]:.2f}. Recomputed.",
              "WARNING")
    cf.loc[mismatch, "net_cash_flow"] = computed.loc[mismatch]
    return cf


# --------------------------------------------------------------------------
# DQ-10 Non-Negative Fixed Assets (WARNING) — coerce negatives to 0
# --------------------------------------------------------------------------
def _dq10_non_negative_fixed_assets(bs: pd.DataFrame, failures: list) -> pd.DataFrame:
    bs = bs.copy()
    negative_mask = bs["fixed_assets"].fillna(0) < 0
    for idx in bs.index[negative_mask]:
        row = bs.loc[idx]
        _flag(failures, "DQ-10", "balancesheet", row["company_id"], row["year"],
              "fixed_assets", f"Negative fixed_assets coerced to 0 (was {row['fixed_assets']})", "WARNING")
    bs.loc[negative_mask, "fixed_assets"] = 0
    return bs


# --------------------------------------------------------------------------
# DQ-11 Tax Rate Range (WARNING)
# --------------------------------------------------------------------------
def _dq11_tax_rate_range(pl: pd.DataFrame, failures: list) -> pd.Series:
    flagged = ~pl["tax_percentage"].between(0, 60) & pl["tax_percentage"].notna()
    for idx in pl.index[flagged]:
        row = pl.loc[idx]
        _flag(failures, "DQ-11", "profitandloss", row["company_id"], row["year"],
              "tax_percentage", f"Tax rate out of [0,60] range: {row['tax_percentage']}", "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-12 Dividend Payout Cap (WARNING)
# --------------------------------------------------------------------------
def _dq12_dividend_payout_cap(pl: pd.DataFrame, failures: list) -> pd.Series:
    flagged = pl["dividend_payout"].fillna(0) > 200
    for idx in pl.index[flagged]:
        row = pl.loc[idx]
        _flag(failures, "DQ-12", "profitandloss", row["company_id"], row["year"],
              "dividend_payout", f"Dividend payout >200%: {row['dividend_payout']}", "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-13 URL Validity (documents) (WARNING) — best-effort, network optional
# --------------------------------------------------------------------------
def _dq13_url_validity(docs: pd.DataFrame, failures: list) -> pd.Series:
    docs_valid = pd.Series([None] * len(docs), index=docs.index, dtype="object")

    if not VALIDATE_URLS:
        logger.info("DQ-13: live URL validation disabled (VALIDATE_DOCUMENT_URLS not set). "
                    "Marking all Annual_Report URLs as unchecked.")
        return docs_valid

    import requests  # imported lazily; only needed when live-checking

    for idx, row in docs.iterrows():
        url = row.get("annual_report_url") or row.get("Annual_Report")
        if not isinstance(url, str) or not url.startswith("http"):
            docs_valid.loc[idx] = False
            continue
        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            ok = resp.status_code == 200
            docs_valid.loc[idx] = ok
            if not ok:
                _flag(failures, "DQ-13", "documents", row["company_id"], row.get("year"),
                      "annual_report_url", f"URL returned status {resp.status_code}", "WARNING")
        except Exception as exc:
            docs_valid.loc[idx] = False
            _flag(failures, "DQ-13", "documents", row["company_id"], row.get("year"),
                  "annual_report_url", f"URL check failed: {exc}", "WARNING")
    return docs_valid


# --------------------------------------------------------------------------
# DQ-14 EPS Sign Consistency (WARNING)
# --------------------------------------------------------------------------
def _dq14_eps_sign_consistency(pl: pd.DataFrame, failures: list) -> pd.Series:
    flagged = (pl["net_profit"].fillna(0) > 0) & (pl["eps"].fillna(0) <= 0)
    for idx in pl.index[flagged]:
        row = pl.loc[idx]
        _flag(failures, "DQ-14", "profitandloss", row["company_id"], row["year"],
              "eps", f"EPS not positive ({row['eps']}) despite positive net_profit ({row['net_profit']})", "WARNING")
    return flagged


# --------------------------------------------------------------------------
# DQ-15 BSE/ASE Balance (ext.) (INFO) — informational counter only
# --------------------------------------------------------------------------
def _dq15_strict_balance_info(bs: pd.DataFrame, dq04_flagged: pd.Series, failures: list) -> int:
    strict_match = (bs["total_assets"] == bs["total_liabilities"])
    info_count = int((strict_match & ~dq04_flagged.reindex(bs.index, fill_value=False)).sum())
    logger.info(f"DQ-15 INFO: {info_count} balance sheet rows are exactly balanced (strict).")
    return info_count


# --------------------------------------------------------------------------
# DQ-16 Coverage Check (WARNING) — each company needs >=5 years of history
# --------------------------------------------------------------------------
def _dq16_coverage_check(pl: pd.DataFrame, bs: pd.DataFrame, cf: pd.DataFrame, failures: list) -> pd.DataFrame:
    counts = pd.DataFrame({
        "pl_years": pl.groupby("company_id")["year"].nunique(),
        "bs_years": bs.groupby("company_id")["year"].nunique(),
        "cf_years": cf.groupby("company_id")["year"].nunique(),
    }).fillna(0)
    low_coverage = counts[(counts["pl_years"] < 5) | (counts["bs_years"] < 5) | (counts["cf_years"] < 5)]
    for company_id, row in low_coverage.iterrows():
        _flag(failures, "DQ-16", "profitandloss/balancesheet/cashflow", company_id, None,
              "year_coverage",
              f"< 5 years history (P&L={int(row['pl_years'])}, BS={int(row['bs_years'])}, CF={int(row['cf_years'])})",
              "WARNING")
    return counts


# --------------------------------------------------------------------------
# Orchestrator
# --------------------------------------------------------------------------
def run_validations(dataframes: dict):
    """Runs all 16 DQ rules against the loaded DataFrames.

    Returns (cleaned_dataframes, validation_failures_df).
    """
    failures = []
    dfs = {k: v.copy() for k, v in dataframes.items()}

    # DQ-01: Company PK uniqueness (checked on the raw 'id' column, then
    # renamed to 'company_id' for consistency with every other table).
    raw_companies = dfs["companies.xlsx"]
    id_col = "id" if "id" in raw_companies.columns else "company_id"
    raw_companies = _dq01_company_pk_uniqueness(raw_companies.rename(columns={id_col: "id"}), failures)
    companies = raw_companies.rename(columns={"id": "company_id"})

    pl = dfs["profitandloss.xlsx"]
    bs = dfs["balancesheet.xlsx"]
    cf = dfs["cashflow.xlsx"]
    analysis = dfs["analysis.xlsx"]
    docs = dfs["documents.xlsx"].rename(columns={"Year": "year", "Annual_Report": "annual_report_url"})
    proscons = dfs["prosandcons.xlsx"]
    sectors = dfs["sectors.xlsx"]
    market_cap = dfs["market_cap.xlsx"]
    stock_prices = dfs["stock_prices.xlsx"]
    peer_groups = dfs["peer_groups.xlsx"]
    fr_reference = dfs["financial_ratios.xlsx"]

    # DQ-08 Ticker format (apply before FK checks so orphan detection uses clean tickers)
    companies = _dq08_ticker_format(companies, "companies", "company_id", failures)
    pl = _dq08_ticker_format(pl, "profitandloss", "company_id", failures)
    bs = _dq08_ticker_format(bs, "balancesheet", "company_id", failures)
    cf = _dq08_ticker_format(cf, "cashflow", "company_id", failures)

    # DQ-02 Annual PK uniqueness (dedupe, keep last)
    pl = _dq02_annual_pk_uniqueness(pl, "profitandloss", failures)
    bs = _dq02_annual_pk_uniqueness(bs, "balancesheet", failures)
    cf = _dq02_annual_pk_uniqueness(cf, "cashflow", failures)

    # DQ-07 Year format (reject unparseable)
    pl = _dq07_year_format(pl, "profitandloss", failures)
    bs = _dq07_year_format(bs, "balancesheet", failures)
    cf = _dq07_year_format(cf, "cashflow", failures)

    valid_ids = set(companies["company_id"])

    # DQ-03 FK integrity (reject orphans) across all child tables
    pl = _dq03_fk_integrity(pl, "profitandloss", valid_ids, failures)
    bs = _dq03_fk_integrity(bs, "balancesheet", valid_ids, failures)
    cf = _dq03_fk_integrity(cf, "cashflow", valid_ids, failures)
    analysis = _dq03_fk_integrity(analysis, "analysis", valid_ids, failures)
    docs = _dq03_fk_integrity(docs, "documents", valid_ids, failures)
    proscons = _dq03_fk_integrity(proscons, "prosandcons", valid_ids, failures)
    sectors = _dq03_fk_integrity(sectors, "sectors", valid_ids, failures)
    market_cap = _dq03_fk_integrity(market_cap, "market_cap", valid_ids, failures)
    stock_prices = _dq03_fk_integrity(stock_prices, "stock_prices", valid_ids, failures)
    peer_groups = _dq03_fk_integrity(peer_groups, "peer_groups", valid_ids, failures)
    fr_reference = _dq03_fk_integrity(fr_reference, "financial_ratios_reference", valid_ids, failures)

    # DQ-04 Balance sheet balance (flag only)
    bs_flagged = _dq04_balance_sheet_balance(bs, failures)

    # DQ-05 OPM cross-check
    _dq05_opm_cross_check(pl, failures)

    # DQ-06 Positive sales (excluding Financials sector)
    financial_tickers = set(sectors.loc[sectors["broad_sector"] == "Financials", "company_id"])
    _dq06_positive_sales(pl, financial_tickers, failures)

    # DQ-09 Net cash check (recompute on mismatch)
    cf = _dq09_net_cash_check(cf, failures)

    # DQ-10 Non-negative fixed assets (coerce)
    bs = _dq10_non_negative_fixed_assets(bs, failures)

    # DQ-11 Tax rate range
    _dq11_tax_rate_range(pl, failures)

    # DQ-12 Dividend payout cap
    _dq12_dividend_payout_cap(pl, failures)

    # DQ-13 URL validity (documents)
    docs["is_url_valid"] = _dq13_url_validity(docs, failures)

    # DQ-14 EPS sign consistency
    _dq14_eps_sign_consistency(pl, failures)

    # DQ-15 Strict balance (informational)
    _dq15_strict_balance_info(bs, bs_flagged, failures)

    # DQ-16 Coverage check
    _dq16_coverage_check(pl, bs, cf, failures)

    cleaned = {
        "companies.xlsx": companies,
        "profitandloss.xlsx": pl,
        "balancesheet.xlsx": bs,
        "cashflow.xlsx": cf,
        "analysis.xlsx": analysis,
        "documents.xlsx": docs,
        "prosandcons.xlsx": proscons,
        "sectors.xlsx": sectors,
        "market_cap.xlsx": market_cap,
        "stock_prices.xlsx": stock_prices,
        "peer_groups.xlsx": peer_groups,
        "financial_ratios.xlsx": fr_reference,
    }

    failures_df = pd.DataFrame(
        failures,
        columns=["rule_id", "table", "company_id", "year", "field", "issue", "severity"],
    )
    n_critical = (failures_df["severity"] == "CRITICAL").sum() if not failures_df.empty else 0
    n_warning = (failures_df["severity"] == "WARNING").sum() if not failures_df.empty else 0
    logger.info(f"Validation complete: {n_critical} CRITICAL, {n_warning} WARNING flags across {len(failures_df)} total rows.")
    print(f"\U0001f6e1\ufe0f DQ Validation complete: {n_critical} CRITICAL, {n_warning} WARNING.")

    return cleaned, failures_df
