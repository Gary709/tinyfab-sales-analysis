-- Headline totals for the 27 real orders.
-- Average order value is rounded half-up to the cent, from integer cents.
-- 204170 cents / 27 orders = 75.6185... dollars, which is $75.62.

SELECT
    COUNT(*) AS orders,
    SUM(total_price_cents) / 100.0 AS revenue_aud,
    COUNT(DISTINCT customer_id) AS customers,
    (
        (SUM(total_price_cents) * 2 + COUNT(*)) / (2 * COUNT(*))
    ) / 100.0 AS avg_order_aud,
    SUM(total_shipping_cents) / 100.0 AS shipping_aud,
    SUM(total_discounts_cents) / 100.0 AS discounts_aud,
    (SELECT SUM(quantity) FROM real_lines) AS spools,
    ROUND(
        (SELECT SUM(quantity) FROM real_lines) * 1.0 / COUNT(*),
        2
    ) AS avg_spools
FROM real_orders;
