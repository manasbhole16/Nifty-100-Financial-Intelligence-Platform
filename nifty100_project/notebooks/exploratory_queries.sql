-- Nifty 100 Financial Intelligence Platform
-- Exploratory SQL queries (Sprint 1, Day 07 deliverable)
-- Run against data/nifty100.db, e.g.:  sqlite3 data/nifty100.db < notebooks/exploratory_queries.sql

-- 1. Row counts across all primary tables
SELECT 'companies' AS table_name, COUNT(*) AS rows FROM companies
UNION ALL SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL SELECT 'documents', COUNT(*) FROM documents
UNION ALL SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL SELECT 'stock_prices', COUNT(*) FROM stock_prices;

-- 2. Companies with the most years of P&L history
SELECT company_id, COUNT(DISTINCT year) AS years_of_history
FROM profitandloss
GROUP BY company_id
ORDER BY years_of_history DESC
LIMIT 10;

-- 3. Top 10 companies by latest-year net profit
SELECT company_id, year, net_profit
FROM profitandloss
WHERE year = (SELECT MAX(year) FROM profitandloss)
ORDER BY net_profit DESC
LIMIT 10;

-- 4. Sector-wise average ROE (from companies table)
SELECT s.broad_sector, ROUND(AVG(c.roe_percentage), 2) AS avg_roe_pct, COUNT(*) AS n_companies
FROM companies c
JOIN sectors s ON s.company_id = c.company_id
GROUP BY s.broad_sector
ORDER BY avg_roe_pct DESC;

-- 5. Companies where the balance sheet does not balance (DQ-04 candidates)
SELECT company_id, year, total_assets, total_liabilities,
       ROUND(ABS(total_assets - total_liabilities), 2) AS abs_diff
FROM balancesheet
WHERE ABS(total_assets - total_liabilities) / NULLIF(total_assets, 0) >= 0.01
ORDER BY abs_diff DESC
LIMIT 20;

-- 6. Highest revenue growth companies (latest vs earliest available year)
WITH bounds AS (
    SELECT company_id, MIN(year) AS first_year, MAX(year) AS last_year
    FROM profitandloss
    GROUP BY company_id
)
SELECT b.company_id,
       p1.sales AS first_year_sales,
       p2.sales AS last_year_sales,
       ROUND((p2.sales - p1.sales) * 1.0 / NULLIF(p1.sales, 0) * 100, 1) AS pct_change
FROM bounds b
JOIN profitandloss p1 ON p1.company_id = b.company_id AND p1.year = b.first_year
JOIN profitandloss p2 ON p2.company_id = b.company_id AND p2.year = b.last_year
WHERE p1.sales > 0
ORDER BY pct_change DESC
LIMIT 10;

-- 7. Companies with negative operating cash flow in the most recent year
SELECT company_id, year, operating_activity
FROM cashflow
WHERE year = (SELECT MAX(year) FROM cashflow)
  AND operating_activity < 0
ORDER BY operating_activity ASC;

-- 8. Sector distribution across the Nifty 100 universe
SELECT broad_sector, COUNT(*) AS n_companies,
       ROUND(SUM(index_weight_pct), 2) AS total_index_weight_pct
FROM sectors
GROUP BY broad_sector
ORDER BY n_companies DESC;

-- 9. Average P/E ratio by market cap category (latest year)
SELECT s.market_cap_category, ROUND(AVG(m.pe_ratio), 2) AS avg_pe
FROM market_cap m
JOIN sectors s ON s.company_id = m.company_id
WHERE m.year = (SELECT MAX(year) FROM market_cap)
GROUP BY s.market_cap_category
ORDER BY avg_pe DESC;

-- 10. Companies with dividend payout above 100% (potential capital allocation flag)
SELECT company_id, year, dividend_payout, net_profit
FROM profitandloss
WHERE dividend_payout > 100
ORDER BY dividend_payout DESC
LIMIT 15;
