-- Spools and revenue by product line.
-- PLA Basic titles are already merged in real_lines.

SELECT
    product_line,
    SUM(quantity) AS spools,
    SUM(discounted_total_cents) / 100.0 AS revenue_aud
FROM real_lines
GROUP BY product_line
ORDER BY spools DESC, product_line;
