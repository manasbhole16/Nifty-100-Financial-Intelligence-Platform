-- Nifty 100 Financial Intelligence Platform: SQLite schema
-- Auto-generated from SQLAlchemy models (src/etl/models.py) after a full pipeline run.
-- Regenerate with: python -m src.etl.pipeline, then dump sqlite_master.

PRAGMA foreign_keys = ON;

CREATE TABLE companies (
	company_id VARCHAR NOT NULL, 
	company_logo VARCHAR, 
	company_name VARCHAR, 
	chart_link VARCHAR, 
	about_company VARCHAR, 
	website VARCHAR, 
	nse_profile VARCHAR, 
	bse_profile VARCHAR, 
	face_value FLOAT, 
	book_value FLOAT, 
	roce_percentage FLOAT, 
	roe_percentage FLOAT, 
	PRIMARY KEY (company_id)
);

CREATE TABLE profitandloss (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year VARCHAR NOT NULL, 
	sales FLOAT, 
	expenses FLOAT, 
	operating_profit FLOAT, 
	opm_percentage FLOAT, 
	other_income FLOAT, 
	interest FLOAT, 
	depreciation FLOAT, 
	profit_before_tax FLOAT, 
	tax_percentage FLOAT, 
	net_profit FLOAT, 
	eps FLOAT, 
	dividend_payout FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_pl_company_year UNIQUE (company_id, year), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE balancesheet (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year VARCHAR NOT NULL, 
	equity_capital FLOAT, 
	reserves FLOAT, 
	borrowings FLOAT, 
	other_liabilities FLOAT, 
	total_liabilities FLOAT, 
	fixed_assets FLOAT, 
	cwip FLOAT, 
	investments FLOAT, 
	other_asset FLOAT, 
	total_assets FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_bs_company_year UNIQUE (company_id, year), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE cashflow (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year VARCHAR NOT NULL, 
	operating_activity FLOAT, 
	investing_activity FLOAT, 
	financing_activity FLOAT, 
	net_cash_flow FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_cf_company_year UNIQUE (company_id, year), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE analysis (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	compounded_sales_growth VARCHAR, 
	compounded_profit_growth VARCHAR, 
	stock_price_cagr VARCHAR, 
	roe VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE documents (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year INTEGER NOT NULL, 
	annual_report_url VARCHAR, 
	is_url_valid BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE prosandcons (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	pros VARCHAR, 
	cons VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE sectors (
	company_id VARCHAR NOT NULL, 
	broad_sector VARCHAR, 
	sub_sector VARCHAR, 
	index_weight_pct FLOAT, 
	market_cap_category VARCHAR, 
	PRIMARY KEY (company_id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE market_cap (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year INTEGER NOT NULL, 
	market_cap_crore FLOAT, 
	enterprise_value_crore FLOAT, 
	pe_ratio FLOAT, 
	pb_ratio FLOAT, 
	ev_ebitda FLOAT, 
	dividend_yield_pct FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_mc_company_year UNIQUE (company_id, year), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE stock_prices (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	date VARCHAR NOT NULL, 
	open_price FLOAT, 
	high_price FLOAT, 
	low_price FLOAT, 
	close_price FLOAT, 
	volume INTEGER, 
	adjusted_close FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_sp_company_date UNIQUE (company_id, date), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE peer_groups (
	id INTEGER NOT NULL, 
	peer_group_name VARCHAR NOT NULL, 
	company_id VARCHAR NOT NULL, 
	is_benchmark BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE financial_ratios_reference (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year VARCHAR NOT NULL, 
	net_profit_margin_pct FLOAT, 
	operating_profit_margin_pct FLOAT, 
	return_on_equity_pct FLOAT, 
	debt_to_equity FLOAT, 
	interest_coverage FLOAT, 
	asset_turnover FLOAT, 
	free_cash_flow_cr FLOAT, 
	capex_cr FLOAT, 
	earnings_per_share FLOAT, 
	book_value_per_share FLOAT, 
	dividend_payout_ratio_pct FLOAT, 
	total_debt_cr FLOAT, 
	cash_from_operations_cr FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

CREATE TABLE financial_ratios (
	id INTEGER NOT NULL, 
	company_id VARCHAR NOT NULL, 
	year VARCHAR NOT NULL, 
	net_profit_margin_pct FLOAT, 
	operating_profit_margin_pct FLOAT, 
	return_on_equity_pct FLOAT, 
	return_on_capital_employed_pct FLOAT, 
	debt_to_equity FLOAT, 
	interest_coverage_ratio FLOAT, 
	asset_turnover FLOAT, 
	revenue_cagr_3yr FLOAT, 
	revenue_cagr_5yr FLOAT, 
	revenue_cagr_10yr FLOAT, 
	pat_cagr_3yr FLOAT, 
	pat_cagr_5yr FLOAT, 
	pat_cagr_10yr FLOAT, 
	eps_cagr_3yr FLOAT, 
	eps_cagr_5yr FLOAT, 
	eps_cagr_10yr FLOAT, 
	revenue_cagr_turnaround BOOLEAN, 
	pat_cagr_turnaround BOOLEAN, 
	eps_cagr_turnaround BOOLEAN, 
	free_cash_flow_cr FLOAT, 
	cfo_pat_ratio FLOAT, 
	capex_intensity_pct FLOAT, 
	fcf_conversion_rate_pct FLOAT, 
	capital_allocation_pattern VARCHAR, 
	is_financial_sector BOOLEAN, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_fr_company_year UNIQUE (company_id, year), 
	FOREIGN KEY(company_id) REFERENCES companies (company_id)
);

