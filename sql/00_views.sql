-- Real paid orders.
-- The export has 35 orders. Eight are not sales:
--   * 6 Shopify test orders (is_test = 1), all customer C01
--   * 2 cancelled and refunded C01 orders for a product titled 'test'
--     ($1.00 on 2026-08-02, $0.01 on 2026-09-24)
-- Those eight fail the filter below. 27 paid orders remain.
-- Test orders are still marked PAID, so is_test has to be checked on its own.
-- The two 'test' product orders are not flagged is_test; the cancelled date,
-- REFUNDED status, and refund amount are what remove them.

CREATE VIEW real_orders AS
SELECT *
FROM orders
WHERE is_test = 0
  AND financial_status = 'PAID'
  AND cancelled_date IS NULL
  AND total_refunded_cents = 0;

-- One row per real line, with a stable product line name.
-- PLA Basic was retitled during this period. Early orders say
-- "TinyFab PLA Basic Filament 1.75mm 1kg", later ones say
-- "TinyFab PLA Basic 1.75mm 1kg". Same 1kg spool.

CREATE VIEW real_lines AS
SELECT
    l.order_id,
    l.product_title,
    l.variant_title,
    l.sku,
    l.quantity,
    l.original_unit_price_cents,
    l.discounted_total_cents,
    o.order_date,
    o.customer_id,
    o.region,
    o.is_act,
    CASE
        WHEN l.product_title LIKE '%PLA Matte%' THEN 'PLA Matte'
        WHEN l.product_title LIKE '%PETG%' THEN 'PETG'
        WHEN l.product_title LIKE '%PLA Basic%' THEN 'PLA Basic'
        ELSE l.product_title
    END AS product_line
FROM order_lines AS l
JOIN real_orders AS o ON o.order_id = l.order_id;

CREATE VIEW order_baskets AS
SELECT
    order_id,
    order_date,
    customer_id,
    SUM(quantity) AS spools
FROM real_lines
GROUP BY order_id, order_date, customer_id;

-- Days from a customer's previous order to this one.
-- One-off customers do not appear.

CREATE VIEW order_gaps AS
WITH sequenced AS (
    SELECT
        customer_id,
        order_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
        ) AS prev_date
    FROM real_orders
)
SELECT
    customer_id,
    order_id,
    prev_date,
    order_date,
    CAST(julianday(order_date) - julianday(prev_date) AS INTEGER) AS days_since_prev
FROM sequenced
WHERE prev_date IS NOT NULL;
