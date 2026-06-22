"""Model training for the three result types.

personalized picks  -> ALS matrix factorization (implicit feedback) shortlists
                        candidates, re-ranked by a neural hybrid model
                        (deep_model.py) blending learned embeddings with
                        engineered side features when one was trained; falls
                        back to item-based CF cosine-similarity for users the
                        ALS model can't confidently score (too few
                        interactions), and popularity as the last resort.
frequently bought together -> association rules (Apriori) over baskets.
popularity fallback  -> frequency + recency weighted ranking, optionally
                        segmented by a retail-pack-provided customer attribute.
"""
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from app.pipeline import deep_model as deep_model_mod

MIN_INTERACTIONS_FOR_ALS = 3
DEEP_MODEL_WEIGHT = 0.5
CANDIDATE_MULTIPLIER = 5


def build_user_item_matrix(txn: pd.DataFrame):
    customers = sorted(txn["customer_id"].unique())
    products = sorted(txn["product_id"].unique())
    cust_idx = {c: i for i, c in enumerate(customers)}
    prod_idx = {p: i for i, p in enumerate(products)}

    counts = txn.groupby(["customer_id", "product_id"]).size().reset_index(name="count")
    rows = counts["customer_id"].map(cust_idx)
    cols = counts["product_id"].map(prod_idx)
    matrix = csr_matrix((counts["count"].values, (rows, cols)), shape=(len(customers), len(products)))
    return matrix, customers, products, cust_idx, prod_idx


def train_als(matrix: csr_matrix, factors: int = 32, iterations: int = 15):
    from implicit.als import AlternatingLeastSquares

    model = AlternatingLeastSquares(factors=factors, iterations=iterations, regularization=0.1)
    model.fit(matrix * 20.0)  # confidence scaling for implicit feedback
    return model


def item_based_cf_scores(matrix: csr_matrix) -> csr_matrix:
    """Item-item cosine similarity over the user-item matrix, used as a
    fallback for customers with too little signal for ALS to be reliable."""
    from sklearn.preprocessing import normalize

    item_vectors = normalize(matrix.T, axis=1)
    similarity = item_vectors @ item_vectors.T
    return similarity.tocsr()


def _minmax(arr: np.ndarray) -> np.ndarray:
    if len(arr) == 0:
        return arr
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.zeros_like(arr, dtype=float)
    return (arr - lo) / (hi - lo)


def personalized_recommendations(
    matrix,
    customers,
    products,
    cust_idx,
    prod_idx,
    als_model,
    item_similarity,
    deep_model=None,
    cust_feat: np.ndarray | None = None,
    prod_feat: np.ndarray | None = None,
    top_k: int = 10,
) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}
    interaction_counts = np.asarray((matrix > 0).sum(axis=1)).ravel()

    for customer, ci in cust_idx.items():
        n_interactions = interaction_counts[ci]
        if n_interactions >= MIN_INTERACTIONS_FOR_ALS:
            candidate_n = min(top_k * CANDIDATE_MULTIPLIER, len(products))
            item_ids, als_scores = als_model.recommend(
                ci, matrix[ci], N=candidate_n, filter_already_liked_items=True
            )
            if deep_model is not None and len(item_ids):
                deep_scores = deep_model_mod.score_items(deep_model, ci, item_ids, cust_feat, prod_feat)
                blended = _minmax(als_scores) * (1 - DEEP_MODEL_WEIGHT) + _minmax(deep_scores) * DEEP_MODEL_WEIGHT
                order = np.argsort(blended)[::-1][:top_k]
                results[customer] = [products[item_ids[o]] for o in order]
            else:
                results[customer] = [products[i] for i in item_ids[:top_k]]
        elif n_interactions > 0:
            owned = matrix[ci].indices
            scores = np.asarray(item_similarity[owned].sum(axis=0)).ravel()
            scores[owned] = -1
            top_items = np.argsort(scores)[::-1][:top_k]
            results[customer] = [products[i] for i in top_items if scores[i] > 0]
        else:
            results[customer] = []
    return results


def association_rules_fbt(txn: pd.DataFrame, top_k: int = 10) -> dict[str, list[str]]:
    """Frequently-bought-together pairs via Apriori over baskets, falling
    back to raw co-occurrence counts when the basket count is too small
    for Apriori's support threshold to find anything."""
    from mlxtend.frequent_patterns import apriori, association_rules
    from mlxtend.preprocessing import TransactionEncoder

    baskets = txn.groupby("transaction_id")["product_id"].apply(list).tolist()
    n_baskets = len(baskets)
    if n_baskets == 0:
        return {}

    te = TransactionEncoder()
    onehot = te.fit_transform(baskets)
    basket_df = pd.DataFrame(onehot, columns=te.columns_)

    min_support = max(2 / n_baskets, 0.01)
    try:
        freq_items = apriori(basket_df, min_support=min_support, use_colnames=True, max_len=2)
        rules = association_rules(freq_items, metric="lift", min_threshold=1.0)
    except Exception:
        rules = pd.DataFrame()

    results: dict[str, list[tuple[str, float]]] = {}
    for _, row in rules.iterrows():
        if len(row["antecedents"]) != 1:
            continue
        antecedent = next(iter(row["antecedents"]))
        for consequent in row["consequents"]:
            results.setdefault(antecedent, []).append((consequent, row["lift"]))

    fbt = {p: [c for c, _ in sorted(v, key=lambda x: -x[1])[:top_k]] for p, v in results.items()}
    return _fill_cooccurrence_fallback(txn, fbt, top_k)


def _fill_cooccurrence_fallback(txn: pd.DataFrame, fbt: dict[str, list[str]], top_k: int) -> dict[str, list[str]]:
    """Products with no association rule above the lift threshold still
    get an entry, built from raw basket co-occurrence counts."""
    all_products = txn["product_id"].unique()
    missing = [p for p in all_products if p not in fbt]
    if not missing:
        return fbt

    basket_groups = txn.groupby("transaction_id")["product_id"].apply(set)
    cooccur: dict[str, dict[str, int]] = {}
    for basket in basket_groups:
        for p in basket:
            if p not in missing:
                continue
            for q in basket:
                if q == p:
                    continue
                cooccur.setdefault(p, {}).setdefault(q, 0)
                cooccur[p][q] += 1

    for p in missing:
        pairs = cooccur.get(p, {})
        top = sorted(pairs.items(), key=lambda x: -x[1])[:top_k]
        fbt[p] = [c for c, _ in top]
    return fbt


def popularity_ranking(txn: pd.DataFrame, customers: pd.DataFrame, segment_key: str | None, top_k: int = 10) -> dict:
    txn = txn.copy()
    txn["timestamp"] = pd.to_datetime(txn["timestamp"], errors="coerce")
    now = txn["timestamp"].max()
    halflife_days = 30.0

    txn["recency_weight"] = 1.0
    valid = txn["timestamp"].notna()
    txn.loc[valid, "recency_weight"] = np.exp(
        -np.log(2) * (now - txn.loc[valid, "timestamp"]).dt.days.clip(lower=0) / halflife_days
    )
    txn["weighted_score"] = txn["quantity"] * txn["recency_weight"]

    overall = (
        txn.groupby("product_id")["weighted_score"].sum().sort_values(ascending=False).head(top_k).index.tolist()
    )
    result = {"overall": overall}

    if segment_key and segment_key in customers.columns:
        merged = txn.merge(customers[["customer_id", segment_key]], on="customer_id", how="left")
        for seg, group in merged.groupby(segment_key):
            ranked = group.groupby("product_id")["weighted_score"].sum().sort_values(ascending=False)
            result[f"segment:{seg}"] = ranked.head(top_k).index.tolist()

    return result
