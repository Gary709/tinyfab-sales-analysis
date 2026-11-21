-- How many orders had each spool count. Counts with no orders are absent.

SELECT
    spools,
    COUNT(*) AS orders
FROM order_baskets
GROUP BY spools
ORDER BY spools;
