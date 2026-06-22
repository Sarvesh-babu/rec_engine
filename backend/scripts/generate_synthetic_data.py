"""Generates a small synthetic Retail dataset for development/testing."""
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sample" / "retail"
random.seed(42)

CATEGORIES = ["electronics", "apparel", "home", "grocery", "beauty"]
BRANDS = ["acme", "globex", "initech", "umbrella", "stark"]
SEGMENTS = ["budget", "regular", "premium"]

SEARCH_TERMS = ["deal", "best", "cheap", "new", "review", "sale", "top rated", "gift"]

N_CUSTOMERS = 60
N_PRODUCTS = 40
N_TRANSACTIONS = 800
N_SESSIONS = 2000
N_SEARCH_LOGS = 500
RETURN_RATE = 0.06
PROMO_PRODUCT_RATE = 0.25


def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame(
        {
            "customer_id": [f"C{i:04d}" for i in range(N_CUSTOMERS)],
            "segment": [random.choice(SEGMENTS) for _ in range(N_CUSTOMERS)],
            "signup_date": [
                (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 500))).date().isoformat()
                for _ in range(N_CUSTOMERS)
            ],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": [f"P{i:04d}" for i in range(N_PRODUCTS)],
            "category": [random.choice(CATEGORIES) for _ in range(N_PRODUCTS)],
            "brand": [random.choice(BRANDS) for _ in range(N_PRODUCTS)],
            "price": [round(random.uniform(5, 250), 2) for _ in range(N_PRODUCTS)],
        }
    )

    # bias some products to co-occur (simulate frequently-bought-together signal)
    affinity_pairs = [(random.randrange(N_PRODUCTS), random.randrange(N_PRODUCTS)) for _ in range(15)]

    rows = []
    start = datetime(2025, 1, 1)
    for t in range(N_TRANSACTIONS):
        cust = random.randrange(N_CUSTOMERS)
        ts = start + timedelta(days=random.randint(0, 170), hours=random.randint(0, 23))
        basket_size = random.choice([1, 1, 2, 2, 3])
        prod = random.randrange(N_PRODUCTS)
        basket = [prod]
        for _ in range(basket_size - 1):
            paired = next((b for a, b in affinity_pairs if a == prod), None)
            basket.append(paired if paired is not None and random.random() < 0.6 else random.randrange(N_PRODUCTS))

        for p in basket:
            rows.append(
                {
                    "transaction_id": f"T{t:05d}",
                    "customer_id": f"C{cust:04d}",
                    "product_id": f"P{p:04d}",
                    "quantity": random.choice([1, 1, 1, 2]),
                    "price": products.loc[p, "price"],
                    "timestamp": ts.isoformat(),
                }
            )

    transactions = pd.DataFrame(rows)

    sessions = _generate_sessions(N_CUSTOMERS, N_PRODUCTS, start)
    returns = _generate_returns(transactions)
    search_logs = _generate_search_logs(N_CUSTOMERS, products, start)
    promotions = _generate_promotions(products, start)

    customers.to_csv(OUT_DIR / "customers.csv", index=False)
    products.to_csv(OUT_DIR / "products.csv", index=False)
    transactions.to_csv(OUT_DIR / "transactions.csv", index=False)
    sessions.to_csv(OUT_DIR / "sessions.csv", index=False)
    returns.to_csv(OUT_DIR / "returns.csv", index=False)
    search_logs.to_csv(OUT_DIR / "search_logs.csv", index=False)
    promotions.to_csv(OUT_DIR / "promotions.csv", index=False)

    print(
        f"Wrote {len(customers)} customers, {len(products)} products, {len(transactions)} transaction rows, "
        f"{len(sessions)} session rows, {len(returns)} return rows, {len(search_logs)} search log rows, "
        f"{len(promotions)} promotion rows to {OUT_DIR}"
    )


def _generate_sessions(n_customers: int, n_products: int, start: datetime) -> pd.DataFrame:
    """Browsing events -- more frequent and noisier than purchases (most
    viewed products are never bought)."""
    rows = []
    for s in range(N_SESSIONS):
        cust = random.randrange(n_customers)
        prod = random.randrange(n_products)
        ts = start + timedelta(days=random.randint(0, 170), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        rows.append(
            {
                "session_id": f"S{s:05d}",
                "customer_id": f"C{cust:04d}",
                "product_id": f"P{prod:04d}",
                "timestamp": ts.isoformat(),
            }
        )
    return pd.DataFrame(rows)


def _generate_returns(transactions: pd.DataFrame) -> pd.DataFrame:
    """A small fraction of purchased line items get returned a few days later."""
    sampled = transactions.sample(frac=RETURN_RATE, random_state=42)
    rows = []
    for _, txn in sampled.iterrows():
        purchase_ts = datetime.fromisoformat(txn["timestamp"])
        return_ts = purchase_ts + timedelta(days=random.randint(2, 21))
        rows.append(
            {
                "transaction_id": txn["transaction_id"],
                "product_id": txn["product_id"],
                "customer_id": txn["customer_id"],
                "return_date": return_ts.date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


def _generate_search_logs(n_customers: int, products: pd.DataFrame, start: datetime) -> pd.DataFrame:
    """Search queries built from category/brand vocabulary plus generic terms."""
    rows = []
    for q in range(N_SEARCH_LOGS):
        cust = random.randrange(n_customers)
        prod = products.iloc[random.randrange(len(products))]
        query_kind = random.choice(["category", "brand", "term"])
        if query_kind == "category":
            query = prod["category"]
        elif query_kind == "brand":
            query = prod["brand"]
        else:
            query = f"{random.choice(SEARCH_TERMS)} {prod['category']}"
        ts = start + timedelta(days=random.randint(0, 170), hours=random.randint(0, 23))
        rows.append(
            {
                "customer_id": f"C{cust:04d}",
                "query": query,
                "timestamp": ts.isoformat(),
            }
        )
    return pd.DataFrame(rows)


def _generate_promotions(products: pd.DataFrame, start: datetime) -> pd.DataFrame:
    """A subset of products run a discount campaign for a few weeks."""
    promoted = products.sample(frac=PROMO_PRODUCT_RATE, random_state=7)
    rows = []
    for _, prod in promoted.iterrows():
        promo_start = start + timedelta(days=random.randint(0, 140))
        promo_end = promo_start + timedelta(days=random.randint(7, 28))
        rows.append(
            {
                "product_id": prod["product_id"],
                "discount_pct": random.choice([10, 15, 20, 25, 30]),
                "start_date": promo_start.date().isoformat(),
                "end_date": promo_end.date().isoformat(),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    generate()
