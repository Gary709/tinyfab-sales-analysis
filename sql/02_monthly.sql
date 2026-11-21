-- Revenue, order count, and average order value by month.
-- August starts on the 8th (the 2 Aug order is the $1.00 test, excluded).
-- November stops on 21 Nov, so it is not a full month.

WITH units AS (
    SELECT
        substr(order_date, 1, 7) AS month,
        SUM(quantity) AS spools
    FROM real_lines
    GROUP BY substr(order_date, 1, 7)
)
SELECT
    substr(o.order_date, 1, 7) AS month,
    COUNT(*) AS orders,
    SUM(o.total_price_cents) / 100.0 AS revenue_aud,
    -- Half-up to the cent. August is 29394 cents / 4 = $73.485, so $73.49.
    (
        (SUM(o.total_price_cents) * 2 + COUNT(*)) / (2 * COUNT(*))
    ) / 100.0 AS avg_order_aud,
    u.spools
FROM real_orders AS o
JOIN units AS u ON u.month = substr(o.order_date, 1, 7)
GROUP BY substr(o.order_date, 1, 7)
ORDER BY month;
