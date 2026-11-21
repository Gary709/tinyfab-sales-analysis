-- Canberra local against everywhere else.
-- region is either 'Canberra local' or a state code. No postcodes.

SELECT
    region,
    CASE WHEN is_act = 1 THEN 'local' ELSE 'interstate' END AS area,
    COUNT(*) AS orders,
    SUM(total_price_cents) / 100.0 AS revenue_aud,
    ROUND(
        100.0 * SUM(total_price_cents) / (SELECT SUM(total_price_cents) FROM real_orders),
        2
    ) AS revenue_pct
FROM real_orders
GROUP BY region, is_act
ORDER BY orders DESC, region;
