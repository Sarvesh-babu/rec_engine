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

N_CUSTOMERS = 60
N_PRODUCTS = 40
N_TRANSACTIONS = 800


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

    customers.to_csv(OUT_DIR / "customers.csv", index=False)
    products.to_csv(OUT_DIR / "products.csv", index=False)
    transactions.to_csv(OUT_DIR / "transactions.csv", index=False)
    print(f"Wrote {len(customers)} customers, {len(products)} products, {len(transactions)} transaction rows to {OUT_DIR}")


if __name__ == "__main__":
    generate()
