# pyrefly: ignore [missing-import]
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, ForeignKey, UniqueConstraint
)
from src.etl.database import Base

# ---------------------------------------------------------------------------
# CORE TABLES (7) — companies.xlsx, profitandloss.xlsx, balancesheet.xlsx,
# cashflow.xlsx, analysis.xlsx, documents.xlsx, prosandcons.xlsx
# ---------------------------------------------------------------------------


class Company(Base):
    """Table storing static Nifty 100 company metadata. (companies.xlsx)"""
    __tablename__ = "companies"

    company_id = Column(String, primary_key=True, index=True)
    company_logo = Column(String, nullable=True)
    company_name = Column(String, index=True)
    chart_link = Column(String, nullable=True)
    about_company = Column(String, nullable=True)
    website = Column(String, nullable=True)
    nse_profile = Column(String, nullable=True)
    bse_profile = Column(String, nullable=True)
    face_value = Column(Float, nullable=True)
    book_value = Column(Float, nullable=True)
    roce_percentage = Column(Float, nullable=True)
    roe_percentage = Column(Float, nullable=True)


class ProfitAndLoss(Base):
    """Annual Profit & Loss statements. (profitandloss.xlsx)"""
    __tablename__ = "profitandloss"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_pl_company_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(String, index=True, nullable=False)
    sales = Column(Float, nullable=True)
    expenses = Column(Float, nullable=True)
    operating_profit = Column(Float, nullable=True)
    opm_percentage = Column(Float, nullable=True)
    other_income = Column(Float, nullable=True)
    interest = Column(Float, nullable=True)
    depreciation = Column(Float, nullable=True)
    profit_before_tax = Column(Float, nullable=True)
    tax_percentage = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    dividend_payout = Column(Float, nullable=True)


class BalanceSheet(Base):
    """Annual Balance Sheet. (balancesheet.xlsx)"""
    __tablename__ = "balancesheet"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_bs_company_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(String, index=True, nullable=False)
    equity_capital = Column(Float, nullable=True)
    reserves = Column(Float, nullable=True)
    borrowings = Column(Float, nullable=True)
    other_liabilities = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    fixed_assets = Column(Float, nullable=True)
    cwip = Column(Float, nullable=True)
    investments = Column(Float, nullable=True)
    other_asset = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)


class CashFlow(Base):
    """Annual Cash Flow statements. (cashflow.xlsx)"""
    __tablename__ = "cashflow"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_cf_company_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(String, index=True, nullable=False)
    operating_activity = Column(Float, nullable=True)
    investing_activity = Column(Float, nullable=True)
    financing_activity = Column(Float, nullable=True)
    net_cash_flow = Column(Float, nullable=True)


class Analysis(Base):
    """Pre-computed growth metrics text fields. Partial coverage (~8 cos). (analysis.xlsx)"""
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    compounded_sales_growth = Column(String, nullable=True)
    compounded_profit_growth = Column(String, nullable=True)
    stock_price_cagr = Column(String, nullable=True)
    roe = Column(String, nullable=True)


class Document(Base):
    """Annual report repository links. (documents.xlsx)
    No unique(company_id, year) constraint: the source legitimately has
    more than one link for the same company/year in some rows, and
    DQ-02 dedup is scoped to P&L/BS/CF tables only, not this one."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(Integer, index=True, nullable=False)  # calendar year, not FY string
    annual_report_url = Column(String, nullable=True)
    is_url_valid = Column(Boolean, nullable=True)  # DQ-13; None = not checked


class ProsAndCons(Base):
    """Qualitative investment insights. Partial coverage. (prosandcons.xlsx)"""
    __tablename__ = "prosandcons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    pros = Column(String, nullable=True)
    cons = Column(String, nullable=True)


# ---------------------------------------------------------------------------
# SUPPLEMENTARY TABLES (3 of the 5 that make up the official "10 tables"
# per Module 1 spec) — sectors.xlsx, market_cap.xlsx, stock_prices.xlsx
# ---------------------------------------------------------------------------


class Sector(Base):
    """Company sector mapping. 1:1 with companies. (sectors.xlsx)"""
    __tablename__ = "sectors"

    company_id = Column(String, ForeignKey("companies.company_id"), primary_key=True)
    broad_sector = Column(String, index=True, nullable=True)
    sub_sector = Column(String, nullable=True)
    index_weight_pct = Column(Float, nullable=True)
    market_cap_category = Column(String, nullable=True)


class MarketCap(Base):
    """Annual valuation multiples (simulated). (market_cap.xlsx)"""
    __tablename__ = "market_cap"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_mc_company_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(Integer, index=True, nullable=False)
    market_cap_crore = Column(Float, nullable=True)
    enterprise_value_crore = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    dividend_yield_pct = Column(Float, nullable=True)


class StockPrice(Base):
    """Monthly OHLCV price history (simulated). (stock_prices.xlsx)"""
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("company_id", "date", name="uq_sp_company_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    date = Column(String, index=True, nullable=False)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    adjusted_close = Column(Float, nullable=True)


# ---------------------------------------------------------------------------
# AUXILIARY RAW TABLES (2) — loaded so all 12 source files land somewhere in
# the database (Sprint 1 checklist item), but NOT counted among the
# official "10 tables" enumerated in Module 1 (used by later sprints).
# ---------------------------------------------------------------------------


class PeerGroup(Base):
    """Peer comparison group membership (raw import). (peer_groups.xlsx)
    Full percentile/ranking engine is a Sprint 3 deliverable (Module 4)."""
    __tablename__ = "peer_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    peer_group_name = Column(String, index=True, nullable=False)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    is_benchmark = Column(Boolean, nullable=True)


class FinancialRatioReference(Base):
    """Pre-computed KPI reference table (raw import for cross-validation
    only). (financial_ratios.xlsx) -- NOT the Sprint 2 computed table;
    see FinancialRatio below for that. No unique(company_id, year)
    constraint: this source file itself contains a handful of exact
    duplicate (company_id, year) rows (same messy-data pattern as the
    raw cashflow.xlsx), and it is reference-only, never used as an
    input to the Ratio Engine."""
    __tablename__ = "financial_ratios_reference"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(String, index=True, nullable=False)
    net_profit_margin_pct = Column(Float, nullable=True)
    operating_profit_margin_pct = Column(Float, nullable=True)
    return_on_equity_pct = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)
    asset_turnover = Column(Float, nullable=True)
    free_cash_flow_cr = Column(Float, nullable=True)
    capex_cr = Column(Float, nullable=True)
    earnings_per_share = Column(Float, nullable=True)
    book_value_per_share = Column(Float, nullable=True)
    dividend_payout_ratio_pct = Column(Float, nullable=True)
    total_debt_cr = Column(Float, nullable=True)
    cash_from_operations_cr = Column(Float, nullable=True)




class FinancialRatio(Base):
    """Computed KPI table populated by the Sprint 2 Ratio Engine.
    One row per company-year (union of P&L/BS/CF coverage -- a row
    exists whenever at least one statement has data for that year).
    See src/analytics/ for the formulas."""
    __tablename__ = "financial_ratios"
    __table_args__ = (UniqueConstraint("company_id", "year", name="uq_fr_company_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey("companies.company_id"), index=True, nullable=False)
    year = Column(String, index=True, nullable=False)

    # Profitability (D08)
    net_profit_margin_pct = Column(Float, nullable=True)
    operating_profit_margin_pct = Column(Float, nullable=True)
    opm_cross_check_mismatch = Column(Boolean, nullable=True)
    return_on_equity_pct = Column(Float, nullable=True)
    return_on_capital_employed_pct = Column(Float, nullable=True)  # ROCE
    return_on_assets_pct = Column(Float, nullable=True)  # ROA

    # Leverage & Efficiency (D09)
    debt_to_equity = Column(Float, nullable=True)
    high_leverage_flag = Column(Boolean, nullable=True)
    interest_coverage_ratio = Column(Float, nullable=True)
    icr_label = Column(String, nullable=True)
    icr_at_risk_flag = Column(Boolean, nullable=True)
    net_debt_cr = Column(Float, nullable=True)
    asset_turnover = Column(Float, nullable=True)

    # CAGR Engine (D10) -- Revenue / PAT / EPS, 3/5/10yr windows, each
    # with its own edge-case flag (DECLINE_TO_LOSS / TURNAROUND /
    # BOTH_NEGATIVE / ZERO_BASE / INSUFFICIENT / None-if-normal)
    revenue_cagr_3yr = Column(Float, nullable=True)
    revenue_cagr_3yr_flag = Column(String, nullable=True)
    revenue_cagr_5yr = Column(Float, nullable=True)
    revenue_cagr_5yr_flag = Column(String, nullable=True)
    revenue_cagr_10yr = Column(Float, nullable=True)
    revenue_cagr_10yr_flag = Column(String, nullable=True)
    pat_cagr_3yr = Column(Float, nullable=True)
    pat_cagr_3yr_flag = Column(String, nullable=True)
    pat_cagr_5yr = Column(Float, nullable=True)
    pat_cagr_5yr_flag = Column(String, nullable=True)
    pat_cagr_10yr = Column(Float, nullable=True)
    pat_cagr_10yr_flag = Column(String, nullable=True)
    eps_cagr_3yr = Column(Float, nullable=True)
    eps_cagr_3yr_flag = Column(String, nullable=True)
    eps_cagr_5yr = Column(Float, nullable=True)
    eps_cagr_5yr_flag = Column(String, nullable=True)
    eps_cagr_10yr = Column(Float, nullable=True)
    eps_cagr_10yr_flag = Column(String, nullable=True)

    # Cash Flow KPIs (D11)
    free_cash_flow_cr = Column(Float, nullable=True)
    cfo_quality_score = Column(Float, nullable=True)
    cfo_quality_label = Column(String, nullable=True)
    capex_cr = Column(Float, nullable=True)  # abs(investing_activity) proxy
    capex_intensity_pct = Column(Float, nullable=True)
    capex_intensity_label = Column(String, nullable=True)
    fcf_conversion_rate_pct = Column(Float, nullable=True)
    capital_allocation_pattern = Column(String, nullable=True)
    cfo_sign = Column(String, nullable=True)
    cfi_sign = Column(String, nullable=True)
    cff_sign = Column(String, nullable=True)

    # Day 12 pass-through / derived columns required by the spec's KPI list
    earnings_per_share = Column(Float, nullable=True)
    book_value_per_share = Column(Float, nullable=True)
    dividend_payout_ratio_pct = Column(Float, nullable=True)
    total_debt_cr = Column(Float, nullable=True)  # == borrowings
    cash_from_operations_cr = Column(Float, nullable=True)  # == operating_activity

    # Composite score (D12) -- NOTE: the sprint doc lists this column but
    # does not define its formula. See populate_ratios.py docstring for
    # the documented, transparent methodology used here.
    composite_quality_score = Column(Float, nullable=True)

    # Context flags
    is_financial_sector = Column(Boolean, nullable=True)  # bank/NBFC carve-out (D13)
