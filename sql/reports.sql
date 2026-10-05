-- MamaEarth Growth Intelligence Pipeline
-- Part 1: Business Reports
-- Run after schema.sql and seed_data.sql.

USE mamaearth_growth;


-- ============================================================
-- (a) Overall order and revenue summary
-- Expected: 180 orders, revenue 99860.20 INR, AOV 554.78 INR
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(
        o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_revenue_inr,
    ROUND(
        SUM(
            o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)
        ) / COUNT(*),
        2
    ) AS average_order_value_inr
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;


-- ============================================================
-- (b) Order count by returned status
-- Expected: 180 total orders, 165 non-returned, 15 returned
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    SUM(returned = 0) AS non_returned_orders,
    SUM(returned = 1) AS returned_orders
FROM orders;


-- ============================================================
-- (c) Top customer by total order value
-- Expected: C045 Vihaan
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_order_value_inr
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_order_value_inr DESC
LIMIT 1;


-- ============================================================
-- (d) City-wise order and return analysis
-- Expected:
-- Jaipur    19 orders, 8 returns, 42.1% return rate
-- Lucknow   49 orders, 15 returns, 30.6% return rate
-- Bangalore 33 orders, 8 returns, 24.2% return rate
-- ============================================================

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned = 1) AS returned_orders,
    ROUND(100 * AVG(o.returned), 1) AS return_rate_pct
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
ORDER BY total_orders DESC;


-- ============================================================
-- (e) Top 5 customers by total order value
-- Expected:
-- C043 Reyansh 12920.00
-- C026 Isha     8371.60
-- C008 Meera    4564.60
-- C011 Arjun    4111.00
-- C042 Sanya    3785.00
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(
        o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_order_value_inr
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_order_value_inr DESC
LIMIT 5;


-- ============================================================
-- (f) Category-wise orders and revenue
-- Expected:
-- Haircare      54 orders, 44956.10 INR
-- Skincare      60 orders, 27346.00 INR
-- Babycare      30 orders, 16805.00 INR
-- PersonalCare  36 orders, 10753.10 INR
-- ============================================================

SELECT
    p.category,
    COUNT(*) AS total_orders,
    ROUND(SUM(
        o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100)
    ), 2) AS total_revenue_inr
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_orders DESC;


-- ============================================================
-- (g) Customers whose names start with A
-- ============================================================

SELECT
    customer_id,
    name,
    city,
    city_tier,
    signup_date,
    acquisition_source
FROM customers
WHERE name LIKE 'A%'
ORDER BY name;


-- ============================================================
-- (h) Distinct customer acquisition sources
-- Expected: Ad, Organic, Referral, Social
-- ============================================================

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;


-- ============================================================
-- (i) Add loyalty tier based on city tier
-- City Tier 1 = Gold
-- Other city tiers = Silver
-- Expected: Gold 28, Silver 17
-- ============================================================

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
