"""Load the TinyFab order CSVs, run the SQL, write the charts."""

from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SQL = ROOT / "sql"
CHARTS = ROOT / "charts"

QUERY_FILES = [
    "01_totals.sql",
    "02_monthly.sql",
    "03_units_by_line.sql",
    "04_units_by_line_and_colour.sql",
    "05_repeat_vs_oneoff.sql",
    "06_revenue_by_customer.sql",
    "07_local_vs_interstate.sql",
    "08_units_per_order.sql",
    "09_spools_per_order.sql",
    "10_days_between_orders.sql",
    "11_days_between_summary.sql",
]


def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript((SQL / "00_schema.sql").read_text())
    _load(conn)
    conn.executescript((SQL / "00_views.sql").read_text())
    return conn


def read_query(conn: sqlite3.Connection, name: str) -> pd.DataFrame:
    return pd.read_sql_query((SQL / name).read_text(), conn)


def _load(conn: sqlite3.Connection) -> None:
    orders = pd.read_csv(DATA / "orders.csv", dtype=str, keep_default_na=False)
    lines = pd.read_csv(DATA / "order_lines.csv", dtype=str, keep_default_na=False)
    for column in ("is_test", "is_act"):
        orders[column] = (orders[column].str.lower() == "true").astype(int)
    orders["cancelled_date"] = orders["cancelled_date"].map(_blank_to_none)
    _to_cents(
        orders,
        [
            "total_price",
            "subtotal",
            "total_shipping",
            "total_discounts",
            "total_tax",
            "total_refunded",
        ],
    )
    _to_cents(lines, ["original_unit_price", "discounted_total"])
    lines["quantity"] = lines["quantity"].astype(int)
    _insert(conn, "orders", orders)
    _insert(conn, "order_lines", lines)


def _to_cents(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        frame[f"{column}_cents"] = frame[column].map(lambda value: int(Decimal(value) * 100))
        del frame[column]


def _blank_to_none(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _insert(conn: sqlite3.Connection, table: str, frame: pd.DataFrame) -> None:
    columns = list(frame.columns)
    sql = (
        f"INSERT INTO {table} ({', '.join(columns)}) "
        f"VALUES ({', '.join('?' for _ in columns)})"
    )
    conn.executemany(sql, [_row(record) for record in frame.itertuples(index=False, name=None)])


def _row(record) -> tuple:
    cleaned = []
    for value in record:
        if value is None or (not isinstance(value, str) and pd.isna(value)):
            cleaned.append(None)
        elif isinstance(value, str) and value.strip() == "":
            cleaned.append(None)
        else:
            cleaned.append(value.item() if hasattr(value, "item") else value)
    return tuple(cleaned)


def _plain(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=120)
    plt.close(fig)


def write_charts(conn: sqlite3.Connection) -> None:
    CHARTS.mkdir(exist_ok=True)
    monthly = read_query(conn, "02_monthly.sql")
    by_line = read_query(conn, "03_units_by_line.sql")
    by_colour = read_query(conn, "04_units_by_line_and_colour.sql")
    repeat = read_query(conn, "05_repeat_vs_oneoff.sql")
    baskets = read_query(conn, "09_spools_per_order.sql")

    _chart_revenue(monthly)
    _chart_lines(by_line)
    _chart_pla_basic(by_colour)
    _chart_repeat(repeat)
    _chart_baskets(baskets)


def _chart_revenue(monthly: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    month_names = {"08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov"}
    labels = [month_names[month[5:]] for month in monthly["month"]]
    bars = ax.bar(labels, monthly["revenue_aud"], width=0.72)
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.set_title("Revenue by month")
    ax.set_xlabel("2026 (November stops on the 21st)")
    ax.set_ylabel("AUD")
    ax.set_ylim(0, monthly["revenue_aud"].max() * 1.18)
    _plain(ax)
    _save(fig, "revenue_by_month.png")


def _chart_lines(by_line: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(by_line["product_line"], by_line["spools"], width=0.72)
    ax.bar_label(bars, padding=3)
    ax.set_title("Spools by product")
    ax.set_ylabel("Spools")
    ax.set_ylim(0, by_line["spools"].max() * 1.18)
    _plain(ax)
    _save(fig, "spools_by_product.png")


def _chart_pla_basic(by_colour: pd.DataFrame) -> None:
    pla = by_colour[by_colour["product_line"] == "PLA Basic"].sort_values(
        ["spools", "colour"], ascending=[True, False]
    )
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    bars = ax.barh(pla["colour"], pla["spools"])
    ax.bar_label(bars, padding=3)
    ax.set_title("PLA Basic spools by colour")
    ax.set_xlabel("Spools")
    ax.set_xlim(0, pla["spools"].max() * 1.15)
    _plain(ax)
    _save(fig, "pla_basic_by_colour.png")


def _chart_repeat(repeat: pd.DataFrame) -> None:
    labels = [
        "Repeat" if kind == "repeat" else "One-off" for kind in repeat["customer_type"]
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(labels, repeat["revenue_aud"], width=0.72)
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.set_title("Revenue from repeat and one-off customers")
    ax.set_ylabel("AUD")
    ax.set_ylim(0, repeat["revenue_aud"].max() * 1.18)
    _plain(ax)
    _save(fig, "repeat_vs_oneoff.png")


def _chart_baskets(baskets: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(baskets["spools"].astype(str), baskets["orders"], width=0.72)
    ax.bar_label(bars, padding=3)
    ax.set_title("Spools per order")
    ax.set_xlabel("Spools in the order")
    ax.set_ylabel("Orders")
    ax.set_ylim(0, baskets["orders"].max() * 1.2)
    _plain(ax)
    _save(fig, "spools_per_order.png")


def main() -> None:
    conn = open_db()
    for name in QUERY_FILES:
        frame = read_query(conn, name)
        print(f"\n== {name}")
        print(frame.to_string(index=False))
    write_charts(conn)
    print(f"\nWrote charts to {CHARTS}")


if __name__ == "__main__":
    main()
