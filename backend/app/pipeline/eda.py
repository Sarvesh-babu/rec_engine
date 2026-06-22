"""Vertical-agnostic EDA summary -- consumes whatever schema is active,
makes no assumption about industry-specific columns.
"""
import pandas as pd


def run_eda(dataframes: dict[str, pd.DataFrame]) -> dict:
    txn = dataframes["transactions"]
    customers = dataframes["customers"]
    products = dataframes["products"]

    txn["timestamp"] = pd.to_datetime(txn["timestamp"], errors="coerce")
    date_span_days = None
    if txn["timestamp"].notna().any():
        date_span_days = (txn["timestamp"].max() - txn["timestamp"].min()).days

    summary = {
        "n_transactions": int(len(txn)),
        "n_customers": int(customers["customer_id"].nunique()),
        "n_products": int(products["product_id"].nunique()),
        "n_customers_with_transactions": int(txn["customer_id"].nunique()),
        "n_products_with_transactions": int(txn["product_id"].nunique()),
        "date_span_days": date_span_days,
        "avg_transactions_per_customer": float(txn.groupby("customer_id").size().mean()),
        "avg_quantity": float(txn["quantity"].mean()),
        "avg_price": float(txn["price"].mean()),
        "optional_files_present": [k for k in ["sessions", "returns", "search_logs", "promotions"] if k in dataframes],
        "sparsity": _sparsity(txn, customers, products),
        "top_products": _top_products(txn),
        "transactions_over_time": _transactions_over_time(txn),
        "price_distribution": _price_distribution(txn),
        "basket_size_distribution": _basket_size_distribution(txn),
    }
    return summary


def _top_products(txn: pd.DataFrame, top_n: int = 10) -> list[dict]:
    counts = txn.groupby("product_id").size().sort_values(ascending=False).head(top_n)
    return [{"product_id": p, "count": int(c)} for p, c in counts.items()]


def _transactions_over_time(txn: pd.DataFrame) -> list[dict]:
    valid = txn.dropna(subset=["timestamp"])
    if valid.empty:
        return []
    weekly = valid.set_index("timestamp").resample("W").size()
    return [{"period": str(d.date()), "count": int(c)} for d, c in weekly.items()]


def _price_distribution(txn: pd.DataFrame, n_bins: int = 10) -> list[dict]:
    prices = txn["price"].dropna()
    if prices.empty:
        return []
    counts, edges = pd.cut(prices, bins=min(n_bins, prices.nunique() or 1), retbins=True, duplicates="drop")
    hist = counts.value_counts().sort_index()
    return [
        {"range": f"{interval.left:.2f}-{interval.right:.2f}", "count": int(c)}
        for interval, c in hist.items()
    ]


def _basket_size_distribution(txn: pd.DataFrame) -> list[dict]:
    sizes = txn.groupby("transaction_id").size().value_counts().sort_index()
    return [{"basket_size": int(s), "count": int(c)} for s, c in sizes.items()]


def category_breakdown(txn: pd.DataFrame, products: pd.DataFrame, category_key: str) -> list[dict]:
    """Generic groupby driven by a column name the industry pack supplies --
    the core EDA module never hardcodes a column like 'category' itself."""
    merged = txn.merge(products[["product_id", category_key]], on="product_id", how="left")
    counts = merged.groupby(category_key).size().sort_values(ascending=False)
    return [{"category": str(k), "count": int(c)} for k, c in counts.items()]


def segment_breakdown(txn: pd.DataFrame, customers: pd.DataFrame, segment_key: str) -> list[dict]:
    merged = txn.merge(customers[["customer_id", segment_key]], on="customer_id", how="left")
    counts = merged.groupby(segment_key).size().sort_values(ascending=False)
    return [{"segment": str(k), "count": int(c)} for k, c in counts.items()]


def _sparsity(txn: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> float:
    n_cust = customers["customer_id"].nunique()
    n_prod = products["product_id"].nunique()
    if n_cust == 0 or n_prod == 0:
        return 1.0
    n_interactions = txn[["customer_id", "product_id"]].drop_duplicates().shape[0]
    return 1.0 - (n_interactions / (n_cust * n_prod))
