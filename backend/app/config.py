from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RUNS_DIR = BASE_DIR / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = ["transactions", "customers", "products"]
OPTIONAL_FILES = ["sessions", "returns", "search_logs", "promotions"]

MIN_TRANSACTION_ROWS = 50
MIN_CUSTOMERS = 5
MIN_PRODUCTS = 5

TOP_K_DEFAULT = 10
