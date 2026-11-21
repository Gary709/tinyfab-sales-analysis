-- Customers with 2 or more orders, against customers with one.
-- revenue_pct is the share of real-order revenue, rounded to 2 d.p.

WITH per_customer AS (
    SELECT
        customer_id,
        COUNT(*) AS orders,
        SUM(total_price_cents) AS revenue_cents
    FROM real_orders
    GROUP BY customer_id
)
SELECT
    CASE WHEN orders >= 2 THEN 'repeat' ELSE 'one-off' END AS customer_type,
    COUNT(*) AS customers,
    SUM(orders) AS orders,
    SUM(revenue_cents) / 100.0 AS revenue_aud,
    ROUND(
        100.0 * SUM(revenue_cents) / (SELECT SUM(revenue_cents) FROM per_customer),
        2
    ) AS revenue_pct
FROM per_customer
GROUP BY customer_type
ORDER BY revenue_aud DESC;
