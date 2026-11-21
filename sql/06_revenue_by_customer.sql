-- Revenue per anonymised customer id. No names.

SELECT
    customer_id,
    COUNT(*) AS orders,
    SUM(total_price_cents) / 100.0 AS revenue_aud,
    ROUND(
        100.0 * SUM(total_price_cents) / (SELECT SUM(total_price_cents) FROM real_orders),
        2
    ) AS revenue_pct
FROM real_orders
GROUP BY customer_id
ORDER BY revenue_aud DESC, customer_id;
