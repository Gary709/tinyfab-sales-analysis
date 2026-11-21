-- Basket size. median_spools is the middle order when sorted by spools
-- (27 orders, so the 14th). Single-spool orders are counted beside it.

SELECT
    COUNT(*) AS orders,
    SUM(spools) AS spools,
    ROUND(AVG(spools), 2) AS avg_spools,
    (
        SELECT spools
        FROM order_baskets
        ORDER BY spools, order_id
        LIMIT 1
        OFFSET (SELECT COUNT(*) / 2 FROM order_baskets)
    ) AS median_spools,
    MIN(spools) AS min_spools,
    MAX(spools) AS max_spools,
    SUM(CASE WHEN spools = 1 THEN 1 ELSE 0 END) AS single_spool_orders
FROM order_baskets;
