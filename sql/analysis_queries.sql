
-- ============================================
-- FINSIGHT FINANCIAL ANALYTICS
-- BUSINESS ANALYSIS QUERIES
-- ============================================

-- 1. Overall financial performance
SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        100.0 * SUM(profit) / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct
FROM financial_data;


-- 2. Country-wise performance
SELECT
    country,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        100.0 * SUM(profit) / NULLIF(SUM(sales), 0),
        2
    ) AS profit_margin_pct
FROM financial_data
GROUP BY country
ORDER BY total_sales DESC;


-- 3. Product-wise profitability
SELECT
    product,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM financial_data
GROUP BY product
ORDER BY total_profit DESC;


-- 4. Segment-wise performance
SELECT
    segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM financial_data
GROUP BY segment
ORDER BY total_profit DESC;


-- 5. Monthly sales and profit
SELECT
    strftime('%Y-%m', date) AS sales_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM financial_data
WHERE date IS NOT NULL
GROUP BY strftime('%Y-%m', date)
ORDER BY sales_month;


-- 6. Discount band analysis
SELECT
    COALESCE(discount_band, 'Unknown') AS discount_band,
    COUNT(*) AS record_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM financial_data
GROUP BY COALESCE(discount_band, 'Unknown')
ORDER BY total_sales DESC;


-- 7. Highest-profit records
SELECT
    date,
    country,
    product,
    sales,
    profit
FROM financial_data
ORDER BY profit DESC
LIMIT 10;


-- 8. Data quality check
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END)
        AS missing_sales,
    SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END)
        AS missing_profit,
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END)
        AS missing_dates
FROM financial_data;
