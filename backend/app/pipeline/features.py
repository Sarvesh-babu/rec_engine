"""Adaptive feature engineering: behavioral/temporal features are always
computed; optional feature groups activate only when their source file
was uploaded. Gates fail soft -- a missing optional file just skips that
feature group rather than erroring the run.
"""
import pandas as pd


def build_features(dataframes: dict[str, pd.DataFrame]) -> dict:
    txn = dataframes["transactions"].copy()
    txn["timestamp"] = pd.to_datetime(txn["timestamp"], errors="coerce")

    features: dict = {}
    features["behavioral"] = _behavioral_features(txn)
    features["temporal"] = _temporal_features(txn)

    if "sessions" in dataframes:
        features["session_affinity"] = _session_affinity(dataframes["sessions"])
    if "returns" in dataframes:
        features["returns_adjusted_demand"] = _returns_adjusted_demand(txn, dataframes["returns"])
    if "search_logs" in dataframes:
        features["search_intent"] = _search_intent(dataframes["search_logs"])
    if "promotions" in dataframes:
        features["promotion_sensitivity"] = _promotion_sensitivity(txn, dataframes["promotions"])

    return features


def _behavioral_features(txn: pd.DataFrame) -> pd.DataFrame:
    agg = txn.groupby("customer_id").agg(
        total_spend=("price", lambda s: float((s * txn.loc[s.index, "quantity"]).sum())),
        n_orders=("transaction_id", "nunique"),
        n_distinct_products=("product_id", "nunique"),
    ).reset_index()
    return agg


def _temporal_features(txn: pd.DataFrame) -> pd.DataFrame:
    valid = txn.dropna(subset=["timestamp"])
    if valid.empty:
        return pd.DataFrame(columns=["customer_id", "recency_days", "last_purchase"])
    now = valid["timestamp"].max()
    agg = valid.groupby("customer_id")["timestamp"].max().reset_index()
    agg["recency_days"] = (now - agg["timestamp"]).dt.days
    agg = agg.rename(columns={"timestamp": "last_purchase"})
    return agg


def _session_affinity(sessions: pd.DataFrame) -> pd.DataFrame:
    return sessions.groupby(["customer_id", "product_id"]).size().reset_index(name="session_views")


def _returns_adjusted_demand(txn: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    sold = txn.groupby("product_id")["quantity"].sum().rename("units_sold")
    returned = returns.groupby("product_id").size().rename("units_returned")
    out = pd.concat([sold, returned], axis=1).fillna(0).reset_index()
    out["net_demand"] = out["units_sold"] - out["units_returned"]
    return out


def _search_intent(search_logs: pd.DataFrame) -> pd.DataFrame:
    return search_logs.groupby("customer_id")["query"].count().reset_index(name="n_searches")


def _promotion_sensitivity(txn: pd.DataFrame, promotions: pd.DataFrame) -> pd.DataFrame:
    promoted_products = set(promotions["product_id"])
    txn = txn.copy()
    txn["was_promoted"] = txn["product_id"].isin(promoted_products)
    return txn.groupby("customer_id")["was_promoted"].mean().reset_index(name="promo_purchase_rate")
