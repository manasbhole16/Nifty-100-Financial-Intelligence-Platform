"""
Populates the `financial_ratios` table for every company-year in the
database. Sprint 2, Days 12-13 -- rewritten to match the authoritative
day-by-day sprint document exactly.

Run directly:  python -m src.analytics.populate_ratios

Outputs:
  - financial_ratios table (SQLite) -- one row per company-year
    (union of P&L/BS/CF coverage, so a company-year with only 2 of the
    3 statements still gets a row with whichever KPIs are computable)
  - output/capital_allocation.csv -- company_id, year, cfo_sign, cfi_sign,
    cff_sign, pattern_label (exact column set from Day 11)
  - output/ratio_edge_cases.log -- every KPI that could not be computed
    (and why), PLUS the Day 13 ROCE/ROE cross-check anomalies

composite_quality_score methodology (D12 lists this column but the
sprint doc does not define a formula for it): this is a documented,
transparent 0-100 blend of five 0-100 sub-scores -- profitability
(ROE), capital efficiency (ROCE), interest-coverage safety, cash-flow
quality (CFO Quality Score), and leverage (D/E, inverted) -- averaged
over whichever sub-scores are available for that company-year. It is
NOT a formula given in the spec; treat it as a reasonable starting
point, not a source-of-truth definition.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

from src.etl.database import engine
from src.etl.logger import get_logger
from src.analytics import ratios
from src.analytics.cagr import compute_all_cagr_windows
from src.analytics import cashflow_kpis as cfk

logger = get_logger(__name__)

OUTPUT_DIR = Path("output")

CFO_QUALITY_TRAILING_YEARS = 5
ROCE_ROE_ANOMALY_THRESHOLD_PCT = 5.0


def _load_source_tables():
    pl = pd.read_sql("SELECT * FROM profitandloss", engine)
    bs = pd.read_sql("SELECT * FROM balancesheet", engine)
    cf = pd.read_sql("SELECT * FROM cashflow", engine)
    sectors = pd.read_sql("SELECT company_id, broad_sector FROM sectors", engine)
    companies = pd.read_sql("SELECT company_id, roce_percentage, roe_percentage, book_value FROM companies", engine)
    return pl, bs, cf, sectors, companies


def _compute_composite_quality_score(roe, roce, icr_value, icr_label, cfo_quality, de_ratio):
    scores = []

    if roe is not None:
        scores.append(max(0.0, min(roe, 40.0)) / 40.0 * 100)

    if roce is not None:
        scores.append(max(0.0, min(roce, 40.0)) / 40.0 * 100)

    if icr_label == "Debt Free":
        scores.append(100.0)
    elif icr_value is not None:
        scores.append(max(0.0, min(icr_value, 10.0)) / 10.0 * 100)

    if cfo_quality is not None:
        if cfo_quality > 1.0:
            scores.append(100.0)
        elif cfo_quality >= 0.5:
            scores.append(70.0)
        else:
            scores.append(30.0)

    if de_ratio is not None:
        scores.append(100.0 - max(0.0, min(de_ratio, 5.0)) / 5.0 * 100)

    if not scores:
        return None
    return round(sum(scores) / len(scores), 2)


def _categorise_anomaly(diff_pct: float) -> str:
    """Heuristic-only categorisation for Day 13's anomaly review -- the
    spec asks for anomalies to be bucketed as 'data source issue',
    'version difference', or 'formula discrepancy' but doesn't define
    how to tell them apart. This is a documented judgement call, not a
    certain diagnosis: small gaps are treated as timing/version
    differences, larger ones as likely methodology (formula)
    discrepancies between the source snapshot and our engine."""
    if diff_pct <= 15:
        return "version difference"
    return "formula discrepancy"


def populate_financial_ratios():
    logger.info("Starting Financial Ratio Engine population run.")
    print("\U0001f4ca Running Financial Ratio Engine (Sprint 2)...")

    OUTPUT_DIR.mkdir(exist_ok=True)
    pl, bs, cf, sectors, companies = _load_source_tables()

    financial_tickers = set(sectors.loc[sectors["broad_sector"] == "Financials", "company_id"])
    roce_ref = dict(zip(companies["company_id"], companies["roce_percentage"]))
    roe_ref = dict(zip(companies["company_id"], companies["roe_percentage"]))

    edge_cases = []
    anomalies = []
    rows_out = []
    alloc_rows = []

    company_ids = sorted(set(pl["company_id"]) | set(bs["company_id"]) | set(cf["company_id"]))

    for company_id in company_ids:
        is_fin = company_id in financial_tickers

        pl_c = pl[pl["company_id"] == company_id].sort_values("year")
        bs_c = bs[bs["company_id"] == company_id].sort_values("year")
        cf_c = cf[cf["company_id"] == company_id].sort_values("year")

        pl_years = sorted(pl_c["year"].tolist())

        sales_by_year = dict(zip(pl_c["year"], pl_c["sales"]))
        net_profit_by_year = dict(zip(pl_c["year"], pl_c["net_profit"]))
        eps_by_year = dict(zip(pl_c["year"], pl_c["eps"]))

        pl_by_year = {row["year"]: row for _, row in pl_c.iterrows()}
        bs_by_year = {row["year"]: row for _, row in bs_c.iterrows()}
        cf_by_year = {row["year"]: row for _, row in cf_c.iterrows()}

        # Union of every year that appears in ANY of the 3 statements
        all_years = sorted(set(pl_by_year) | set(bs_by_year) | set(cf_by_year))

        for year in all_years:
            pl_row = pl_by_year.get(year)
            bs_row = bs_by_year.get(year)
            cf_row = cf_by_year.get(year)

            def log_edge(metric, reason):
                edge_cases.append({"company_id": company_id, "year": year, "metric": metric, "reason": reason})

            # --- Profitability (D08) ---
            npm = opm = roe = roce = roa = None
            opm_mismatch = None
            if pl_row is not None:
                npm = ratios.net_profit_margin(pl_row["net_profit"], pl_row["sales"])
                if npm is None:
                    log_edge("net_profit_margin_pct", "sales is zero/missing")
                opm = ratios.operating_profit_margin(pl_row["operating_profit"], pl_row["sales"])
                if opm is None:
                    log_edge("operating_profit_margin_pct", "sales is zero/missing")
                opm_mismatch = ratios.opm_cross_check_mismatch(opm, pl_row.get("opm_percentage"))
                if opm_mismatch:
                    log_edge("operating_profit_margin_pct", f"cross-check mismatch vs source opm_percentage (>1pp): computed={opm}, source={pl_row.get('opm_percentage')}")
            if pl_row is not None and bs_row is not None:
                roe = ratios.return_on_equity(pl_row["net_profit"], bs_row["equity_capital"], bs_row["reserves"])
                if roe is None:
                    log_edge("return_on_equity_pct", "shareholders' equity is zero/negative or missing")
                roce = ratios.return_on_capital_employed(pl_row["operating_profit"], bs_row["equity_capital"], bs_row["reserves"], bs_row["borrowings"])
                if roce is None:
                    log_edge("return_on_capital_employed_pct", "capital employed (equity+reserves+borrowings) is zero/negative or missing")
                roa = ratios.return_on_assets(pl_row["net_profit"], bs_row["total_assets"])
                if roa is None:
                    log_edge("return_on_assets_pct", "total_assets is zero/missing")

            # --- Leverage & Efficiency (D09) ---
            de = icr_value = icr_label = ndebt = at = None
            hl_flag = icr_risk_flag = False
            if bs_row is not None:
                de = ratios.debt_to_equity(bs_row["borrowings"], bs_row["equity_capital"], bs_row["reserves"])
                if de is None:
                    log_edge("debt_to_equity", "shareholders' equity is zero/negative or missing")
                hl_flag = ratios.high_leverage_flag(de, is_fin)
                ndebt = ratios.net_debt(bs_row["borrowings"], bs_row["investments"])
            if pl_row is not None:
                icr_value, icr_label = ratios.interest_coverage_ratio(pl_row["operating_profit"], pl_row["other_income"], pl_row["interest"])
                if icr_label == "Debt Free":
                    log_edge("interest_coverage_ratio", "debt-free company (interest expense is zero)")
                icr_risk_flag = ratios.icr_at_risk_flag(icr_value)
                if icr_risk_flag:
                    log_edge("interest_coverage_ratio", f"ICR < 1.5 (value={icr_value:.2f}): at risk of not covering interest")
            if pl_row is not None and bs_row is not None:
                at = ratios.asset_turnover(pl_row["sales"], bs_row["total_assets"])
                if at is None:
                    log_edge("asset_turnover", "total_assets is zero/missing")

            # --- CAGR Engine (D10) ---
            revenue_cagr = compute_all_cagr_windows(pl_years, sales_by_year, year) if year in pl_years else {f"cagr_{w}yr": None for w in (3, 5, 10)} | {f"cagr_{w}yr_flag": "INSUFFICIENT" for w in (3, 5, 10)}
            pat_cagr = compute_all_cagr_windows(pl_years, net_profit_by_year, year) if year in pl_years else {f"cagr_{w}yr": None for w in (3, 5, 10)} | {f"cagr_{w}yr_flag": "INSUFFICIENT" for w in (3, 5, 10)}
            eps_cagr = compute_all_cagr_windows(pl_years, eps_by_year, year) if year in pl_years else {f"cagr_{w}yr": None for w in (3, 5, 10)} | {f"cagr_{w}yr_flag": "INSUFFICIENT" for w in (3, 5, 10)}
            for label, res in [("revenue", revenue_cagr), ("pat", pat_cagr), ("eps", eps_cagr)]:
                for w in (3, 5, 10):
                    flag = res[f"cagr_{w}yr_flag"]
                    if flag:
                        log_edge(f"{label}_cagr_{w}yr", flag)

            # --- Cash Flow KPIs (D11) ---
            fcf = capex_proxy = capex_int = capex_label = fcf_conv = None
            cfo_sign = cfi_sign = cff_sign = "?"
            pattern = "Mixed"
            cfo_q_score = cfo_q_label = None
            if cf_row is not None:
                fcf = cfk.free_cash_flow(cf_row["operating_activity"], cf_row["investing_activity"])
                cfo_sign = cfk._sign(cf_row["operating_activity"])
                cfi_sign = cfk._sign(cf_row["investing_activity"])
                cff_sign = cfk._sign(cf_row["financing_activity"])

                # 5-year trailing CFO/PAT quality score
                cf_years_sorted = sorted(cf_by_year.keys())
                if year in cf_years_sorted:
                    idx = cf_years_sorted.index(year)
                    trailing_years = cf_years_sorted[max(0, idx - CFO_QUALITY_TRAILING_YEARS + 1): idx + 1]
                    trailing_ratios = []
                    for ty in trailing_years:
                        cf_t = cf_by_year.get(ty)
                        pl_t = pl_by_year.get(ty)
                        if cf_t is not None and pl_t is not None:
                            r = cfk.single_year_cfo_pat_ratio(cf_t["operating_activity"], pl_t["net_profit"])
                            if r is not None:
                                trailing_ratios.append(r)
                    cfo_q_score, cfo_q_label = cfk.cfo_quality_score(trailing_ratios)
                    if cfo_q_score is None:
                        log_edge("cfo_quality_score", "no years with positive PAT in trailing window")

                if pl_row is not None:
                    capex_int, capex_label = cfk.capex_intensity(cf_row["investing_activity"], pl_row["sales"])
                    capex_proxy = abs(cf_row["investing_activity"]) if cf_row["investing_activity"] is not None else None
                    fcf_conv = cfk.fcf_conversion_rate(fcf, pl_row["operating_profit"])
                    if fcf_conv is None:
                        log_edge("fcf_conversion_rate_pct", "operating_profit is zero/missing")

                pattern = cfk.classify_capital_allocation(
                    cf_row["operating_activity"], cf_row["investing_activity"], cf_row["financing_activity"], cfo_q_score,
                )
            else:
                log_edge("capital_allocation_pattern", "no cash flow statement for this year")

            composite = _compute_composite_quality_score(roe, roce, icr_value, icr_label, cfo_q_score, de)

            book_value_per_share = None
            if pl_row is not None and bs_row is not None and pl_row["eps"] not in (None, 0) and pl_row["net_profit"] not in (None, 0):
                shares_outstanding = pl_row["net_profit"] / pl_row["eps"]
                if shares_outstanding:
                    book_value_per_share = (bs_row["equity_capital"] + bs_row["reserves"]) / shares_outstanding

            rows_out.append({
                "company_id": company_id, "year": year,
                "net_profit_margin_pct": npm, "operating_profit_margin_pct": opm,
                "opm_cross_check_mismatch": opm_mismatch,
                "return_on_equity_pct": roe, "return_on_capital_employed_pct": roce,
                "return_on_assets_pct": roa,
                "debt_to_equity": de, "high_leverage_flag": hl_flag,
                "interest_coverage_ratio": icr_value, "icr_label": icr_label,
                "icr_at_risk_flag": icr_risk_flag, "net_debt_cr": ndebt,
                "asset_turnover": at,
                "revenue_cagr_3yr": revenue_cagr["cagr_3yr"], "revenue_cagr_3yr_flag": revenue_cagr["cagr_3yr_flag"],
                "revenue_cagr_5yr": revenue_cagr["cagr_5yr"], "revenue_cagr_5yr_flag": revenue_cagr["cagr_5yr_flag"],
                "revenue_cagr_10yr": revenue_cagr["cagr_10yr"], "revenue_cagr_10yr_flag": revenue_cagr["cagr_10yr_flag"],
                "pat_cagr_3yr": pat_cagr["cagr_3yr"], "pat_cagr_3yr_flag": pat_cagr["cagr_3yr_flag"],
                "pat_cagr_5yr": pat_cagr["cagr_5yr"], "pat_cagr_5yr_flag": pat_cagr["cagr_5yr_flag"],
                "pat_cagr_10yr": pat_cagr["cagr_10yr"], "pat_cagr_10yr_flag": pat_cagr["cagr_10yr_flag"],
                "eps_cagr_3yr": eps_cagr["cagr_3yr"], "eps_cagr_3yr_flag": eps_cagr["cagr_3yr_flag"],
                "eps_cagr_5yr": eps_cagr["cagr_5yr"], "eps_cagr_5yr_flag": eps_cagr["cagr_5yr_flag"],
                "eps_cagr_10yr": eps_cagr["cagr_10yr"], "eps_cagr_10yr_flag": eps_cagr["cagr_10yr_flag"],
                "free_cash_flow_cr": fcf,
                "cfo_quality_score": cfo_q_score, "cfo_quality_label": cfo_q_label,
                "capex_cr": capex_proxy, "capex_intensity_pct": capex_int, "capex_intensity_label": capex_label,
                "fcf_conversion_rate_pct": fcf_conv,
                "capital_allocation_pattern": pattern,
                "cfo_sign": cfo_sign, "cfi_sign": cfi_sign, "cff_sign": cff_sign,
                "earnings_per_share": pl_row["eps"] if pl_row is not None else None,
                "book_value_per_share": book_value_per_share,
                "dividend_payout_ratio_pct": pl_row["dividend_payout"] if pl_row is not None else None,
                "total_debt_cr": bs_row["borrowings"] if bs_row is not None else None,
                "cash_from_operations_cr": cf_row["operating_activity"] if cf_row is not None else None,
                "composite_quality_score": composite,
                "is_financial_sector": is_fin,
            })

            alloc_rows.append({
                "company_id": company_id, "year": year,
                "cfo_sign": cfo_sign, "cfi_sign": cfi_sign, "cff_sign": cff_sign,
                "pattern_label": pattern,
            })

        # --- Day 13: ROCE/ROE cross-check vs static companies.xlsx values (latest year) ---
        if all_years:
            latest_year = all_years[-1]
            latest_row = next((r for r in rows_out if r["company_id"] == company_id and r["year"] == latest_year), None)
            if latest_row is not None:
                src_roce = roce_ref.get(company_id)
                src_roe = roe_ref.get(company_id)
                if latest_row["return_on_capital_employed_pct"] is not None and src_roce is not None:
                    diff = abs(latest_row["return_on_capital_employed_pct"] - src_roce)
                    if diff > ROCE_ROE_ANOMALY_THRESHOLD_PCT:
                        anomalies.append({
                            "company_id": company_id, "year": latest_year, "metric": "ROCE",
                            "computed": round(latest_row["return_on_capital_employed_pct"], 2),
                            "source": src_roce, "diff_pct": round(diff, 2),
                            "category": _categorise_anomaly(diff),
                        })
                if latest_row["return_on_equity_pct"] is not None and src_roe is not None:
                    diff = abs(latest_row["return_on_equity_pct"] - src_roe)
                    if diff > ROCE_ROE_ANOMALY_THRESHOLD_PCT:
                        anomalies.append({
                            "company_id": company_id, "year": latest_year, "metric": "ROE",
                            "computed": round(latest_row["return_on_equity_pct"], 2),
                            "source": src_roe, "diff_pct": round(diff, 2),
                            "category": _categorise_anomaly(diff),
                        })

    ratios_df = pd.DataFrame(rows_out)

    # --- Persist to SQLite (financial_ratios table) ---
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM financial_ratios")
    ratios_df.to_sql("financial_ratios", engine, if_exists="append", index=False)
    logger.info(f"Wrote {len(ratios_df)} rows to financial_ratios.")
    print(f"\u2705 financial_ratios table populated: {len(ratios_df)} company-year rows")

    # --- output/capital_allocation.csv (Day 11 exact column set, every company-year) ---
    alloc_df = pd.DataFrame(alloc_rows).sort_values(["company_id", "year"])
    capital_alloc_path = OUTPUT_DIR / "capital_allocation.csv"
    alloc_df.to_csv(capital_alloc_path, index=False)
    print(f"\u2705 Wrote {capital_alloc_path} ({len(alloc_df)} rows)")

    # --- output/ratio_edge_cases.log ---
    edge_log_path = OUTPUT_DIR / "ratio_edge_cases.log"
    with open(edge_log_path, "w") as f:
        f.write(f"# Ratio Edge Case Log -- generated {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"# Total KPI edge cases logged: {len(edge_cases)}\n")
        f.write(f"# Total Day-13 ROCE/ROE cross-check anomalies: {len(anomalies)}\n\n")
        f.write("## KPI edge cases\n")
        for case in edge_cases:
            f.write(f"[{case['company_id']} | {case['year']}] {case['metric']}: {case['reason']}\n")
        f.write("\n## Day 13: ROCE / ROE cross-check anomalies (computed vs companies.xlsx, latest year, |diff| > 5pp)\n")
        for a in anomalies:
            f.write(
                f"[{a['company_id']} | {a['year']}] {a['metric']}: computed={a['computed']}, "
                f"source={a['source']}, diff={a['diff_pct']}pp, category={a['category']}\n"
            )
    logger.info(f"Wrote {len(edge_cases)} edge cases + {len(anomalies)} anomalies to {edge_log_path}")
    print(f"\u2705 Wrote {len(edge_cases)} edge cases + {len(anomalies)} anomalies to {edge_log_path}")

    return ratios_df, edge_cases, anomalies


if __name__ == "__main__":
    populate_financial_ratios()
