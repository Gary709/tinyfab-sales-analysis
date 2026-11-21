-- Each gap between two consecutive orders from the same customer.

SELECT
    customer_id,
    prev_date,
    order_date,
    days_since_prev
FROM order_gaps
ORDER BY customer_id, order_date;
