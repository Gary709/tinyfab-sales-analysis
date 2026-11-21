"""Checks against the 27 real orders. Figures are the SQL output, in cents."""

import pandas as pd

from analysis import open_db, read_query, QUERY_FILES


def _cents(value) -> int:
    return int(round(float(value) * 100))


def test_queries_return_rows():
    conn = open_db()
    for name in QUERY_FILES:
        frame = read_query(conn, name)
        assert len(frame) >= 1, name


def test_exclusion_leaves_27_orders_and_2041_70():
    conn = open_db()
    totals = read_query(conn, "01_totals.sql").iloc[0]
    assert int(totals["orders"]) == 27
    assert _cents(totals["revenue_aud"]) == 204170
    assert int(totals["customers"]) == 16
    assert _cents(totals["avg_order_aud"]) == 7562
    assert _cents(totals["shipping_aud"]) == 0
    assert _cents(totals["discounts_aud"]) == 0
    assert int(totals["spools"]) == 129
    assert float(totals["avg_spools"]) == 4.78

    excluded = pd.read_sql_query(
        """
        SELECT order_id
        FROM orders
        WHERE order_id NOT IN (SELECT order_id FROM real_orders)
        ORDER BY order_id
        """,
        conn,
    )
    assert excluded["order_id"].tolist() == [
        "O001",
        "O004",
        "O005",
        "O012",
        "O013",
        "O014",
        "O015",
        "O018",
    ]

    customers = pd.read_sql_query(
        "SELECT DISTINCT customer_id FROM real_orders", conn
    )
    assert "C01" not in set(customers["customer_id"])

    titles = pd.read_sql_query(
        "SELECT DISTINCT product_title FROM real_lines", conn
    )
    assert "test" not in set(titles["product_title"])

    mismatch = pd.read_sql_query(
        """
        SELECT o.order_id
        FROM real_orders AS o
        JOIN (
            SELECT order_id, SUM(discounted_total_cents) AS line_cents
            FROM real_lines
            GROUP BY order_id
        ) AS lines ON lines.order_id = o.order_id
        WHERE lines.line_cents != o.total_price_cents
        """,
        conn,
    )
    assert mismatch.empty


def test_monthly_and_product_totals():
    conn = open_db()
    monthly = read_query(conn, "02_monthly.sql")
    assert monthly["month"].tolist() == ["2026-08", "2026-09", "2026-10", "2026-11"]
    assert [_cents(v) for v in monthly["revenue_aud"]] == [29394, 61690, 61383, 51703]
    assert [int(v) for v in monthly["orders"]] == [4, 8, 8, 7]
    assert [_cents(v) for v in monthly["avg_order_aud"]] == [7349, 7711, 7673, 7386]
    assert [int(v) for v in monthly["spools"]] == [18, 39, 39, 33]

    lines = read_query(conn, "03_units_by_line.sql").set_index("product_line")
    assert int(lines.loc["PLA Basic", "spools"]) == 91
    assert _cents(lines.loc["PLA Basic", "revenue_aud"]) == 145092
    assert int(lines.loc["PETG", "spools"]) == 30
    assert _cents(lines.loc["PETG", "revenue_aud"]) == 44686
    assert int(lines.loc["PLA Matte", "spools"]) == 8
    assert _cents(lines.loc["PLA Matte", "revenue_aud"]) == 14392

    colours = read_query(conn, "04_units_by_line_and_colour.sql")
    royal = colours[
        (colours["product_line"] == "PLA Basic") & (colours["colour"] == "Royal Blue")
    ].iloc[0]
    assert int(royal["spools"]) == 22
    assert _cents(royal["revenue_aud"]) == 36236

    prices = pd.read_sql_query(
        """
        SELECT variant_title AS colour, original_unit_price_cents AS cents
        FROM real_lines
        WHERE product_line = 'PLA Basic'
        """,
        conn,
    )
    cheaper = {"Black", "White", "Grey"}
    for colour, cents in zip(prices["colour"], prices["cents"], strict=True):
        if colour in cheaper:
            assert int(cents) in (1330, 1344, 1358)
        else:
            assert int(cents) in (1635, 1649)


def test_repeat_local_and_baskets():
    conn = open_db()
    repeat = read_query(conn, "05_repeat_vs_oneoff.sql").set_index("customer_type")
    assert int(repeat.loc["repeat", "customers"]) == 7
    assert int(repeat.loc["repeat", "orders"]) == 18
    assert _cents(repeat.loc["repeat", "revenue_aud"]) == 164424
    assert float(repeat.loc["repeat", "revenue_pct"]) == 80.53
    assert int(repeat.loc["one-off", "customers"]) == 9
    assert int(repeat.loc["one-off", "orders"]) == 9
    assert _cents(repeat.loc["one-off", "revenue_aud"]) == 39746
    assert float(repeat.loc["one-off", "revenue_pct"]) == 19.47

    top = read_query(conn, "06_revenue_by_customer.sql").iloc[0]
    assert top["customer_id"] == "C02"
    assert int(top["orders"]) == 5
    assert _cents(top["revenue_aud"]) == 107995
    assert float(top["revenue_pct"]) == 52.89

    regions = read_query(conn, "07_local_vs_interstate.sql").set_index("region")
    assert int(regions.loc["Canberra local", "orders"]) == 26
    assert _cents(regions.loc["Canberra local", "revenue_aud"]) == 200572
    assert int(regions.loc["NSW", "orders"]) == 1
    assert _cents(regions.loc["NSW", "revenue_aud"]) == 3598

    basket = read_query(conn, "08_units_per_order.sql").iloc[0]
    assert int(basket["spools"]) == 129
    assert float(basket["avg_spools"]) == 4.78
    assert int(basket["median_spools"]) == 3
    assert int(basket["min_spools"]) == 1
    assert int(basket["max_spools"]) == 19
    assert int(basket["single_spool_orders"]) == 7

    gaps = read_query(conn, "11_days_between_summary.sql").iloc[0]
    assert int(gaps["gaps"]) == 11
    assert float(gaps["avg_days"]) == 22.27
    assert int(gaps["median_days"]) == 23
    assert int(gaps["min_days"]) == 4
    assert int(gaps["max_days"]) == 56
