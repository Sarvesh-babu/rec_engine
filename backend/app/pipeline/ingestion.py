"""Universal schema validation + adaptive ingestion.

Validation happens in two passes that mirror the client-side checks:
1. required files present, required columns present
2. minimum volume thresholds (hard-error gate)

Optional files are loaded if present, skipped (not errored) if absent --
feature engineering gates on their presence later in the pipeline.
"""
import pandas as pd

from app.config import MIN_CUSTOMERS, MIN_PRODUCTS, MIN_TRANSACTION_ROWS, OPTIONAL_FILES, REQUIRED_FILES
from app.schemas import OPTIONAL_COLUMNS, UNIVERSAL_REQUIRED_COLUMNS


class ValidationError(Exception):
    pass


def load_uploaded_files(file_paths: dict[str, str]) -> dict[str, pd.DataFrame]:
    """file_paths: logical name (e.g. 'transactions') -> path on disk."""
    missing_required = [f for f in REQUIRED_FILES if f not in file_paths]
    if missing_required:
        raise ValidationError(f"Missing required file(s): {missing_required}")

    dataframes: dict[str, pd.DataFrame] = {}
    for name in REQUIRED_FILES:
        df = pd.read_csv(file_paths[name])
        missing_cols = [c for c in UNIVERSAL_REQUIRED_COLUMNS[name] if c not in df.columns]
        if missing_cols:
            raise ValidationError(f"'{name}' is missing required column(s): {missing_cols}")
        dataframes[name] = df

    for name in OPTIONAL_FILES:
        if name in file_paths:
            df = pd.read_csv(file_paths[name])
            missing_cols = [c for c in OPTIONAL_COLUMNS[name] if c not in df.columns]
            if missing_cols:
                raise ValidationError(f"optional file '{name}' uploaded but missing column(s): {missing_cols}")
            dataframes[name] = df

    _hard_error_gate(dataframes)
    return dataframes


def _hard_error_gate(dataframes: dict[str, pd.DataFrame]) -> None:
    n_txn = len(dataframes["transactions"])
    n_cust = dataframes["customers"]["customer_id"].nunique()
    n_prod = dataframes["products"]["product_id"].nunique()

    if n_txn < MIN_TRANSACTION_ROWS:
        raise ValidationError(f"Need at least {MIN_TRANSACTION_ROWS} transaction rows, got {n_txn}")
    if n_cust < MIN_CUSTOMERS:
        raise ValidationError(f"Need at least {MIN_CUSTOMERS} unique customers, got {n_cust}")
    if n_prod < MIN_PRODUCTS:
        raise ValidationError(f"Need at least {MIN_PRODUCTS} unique products, got {n_prod}")
