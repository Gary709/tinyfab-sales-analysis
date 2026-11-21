-- Summary of the gaps in sql/10_days_between_orders.sql.
-- median_days is the middle gap (11 gaps, so the 6th).

SELECT
    COUNT(*) AS gaps,
    ROUND(AVG(days_since_prev), 2) AS avg_days,
    (
        SELECT days_since_prev
        FROM order_gaps
        ORDER BY days_since_prev, customer_id, order_date
        LIMIT 1
        OFFSET (SELECT COUNT(*) / 2 FROM order_gaps)
    ) AS median_days,
    MIN(days_since_prev) AS min_days,
    MAX(days_since_prev) AS max_days
FROM order_gaps;
