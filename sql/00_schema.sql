-- Tables match data/orders.csv and data/order_lines.csv.
-- Money is stored as integer cents so sums and averages do not drift.
-- analysis.py loads the CSVs, converts dollars to cents, then creates the views.

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    cancelled_date TEXT,
    is_test INTEGER NOT NULL,
    financial_status TEXT NOT NULL,
    fulfillment_status TEXT,
    currency TEXT NOT NULL,
    total_price_cents INTEGER NOT NULL,
    subtotal_cents INTEGER NOT NULL,
    total_shipping_cents INTEGER NOT NULL,
    total_discounts_cents INTEGER NOT NULL,
    total_tax_cents INTEGER NOT NULL,
    total_refunded_cents INTEGER NOT NULL,
    discount_codes TEXT,
    shipping_method TEXT,
    region TEXT NOT NULL,
    is_act INTEGER NOT NULL,
    source_name TEXT,
    channel TEXT,
    customer_id TEXT NOT NULL
);

CREATE TABLE order_lines (
    order_id TEXT NOT NULL,
    product_title TEXT NOT NULL,
    variant_title TEXT,
    sku TEXT,
    quantity INTEGER NOT NULL,
    original_unit_price_cents INTEGER NOT NULL,
    discounted_total_cents INTEGER NOT NULL,
    currency TEXT NOT NULL
);
