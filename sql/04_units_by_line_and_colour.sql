-- Spools and revenue by product line and colour.
-- Colour is the Shopify variant title.

SELECT
    product_line,
    variant_title AS colour,
    SUM(quantity) AS spools,
    SUM(discounted_total_cents) / 100.0 AS revenue_aud
FROM real_lines
GROUP BY product_line, variant_title
ORDER BY product_line, spools DESC, colour;
