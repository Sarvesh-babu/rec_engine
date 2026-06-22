"""Orchestrates one end-to-end pipeline run: ingest -> validate -> EDA ->
features -> train -> persist. Industry-agnostic except for the single
call into the registry-resolved pack.
"""
from app.pipeline import deep_model as deep_model_mod
from app.pipeline import eda as eda_mod
from app.pipeline import features as features_mod
from app.pipeline import models as models_mod
from app.pipeline import store
from app.pipeline.ingestion import ValidationError, load_uploaded_files
from app.registry import get_pack


def run_pipeline(run_id: str, industry: str, file_paths: dict[str, str]) -> None:
    store.create_run(run_id, industry)
    try:
        pack = get_pack(industry)
        dataframes = load_uploaded_files(file_paths)

        warnings = pack.validate_extension(dataframes["products"], dataframes["customers"])
        eda_summary = eda_mod.run_eda(dataframes)
        eda_summary["warnings"] = warnings

        category_key = pack.category_key(dataframes["products"])
        if category_key:
            eda_summary["category_breakdown"] = eda_mod.category_breakdown(
                dataframes["transactions"], dataframes["products"], category_key
            )
        segment_key_for_eda = pack.popularity_segment_key(dataframes["customers"])
        if segment_key_for_eda:
            eda_summary["segment_breakdown"] = eda_mod.segment_breakdown(
                dataframes["transactions"], dataframes["customers"], segment_key_for_eda
            )

        features = features_mod.build_features(dataframes)

        txn = dataframes["transactions"]
        matrix, customers, products, cust_idx, prod_idx = models_mod.build_user_item_matrix(txn)
        als_model = models_mod.train_als(matrix)
        item_similarity = models_mod.item_based_cf_scores(matrix)

        cust_feat, prod_feat = deep_model_mod.build_side_features(features, dataframes, customers, products)
        deep_model = deep_model_mod.train_neural_model(matrix, cust_feat, prod_feat)

        personalized = models_mod.personalized_recommendations(
            matrix,
            customers,
            products,
            cust_idx,
            prod_idx,
            als_model,
            item_similarity,
            deep_model=deep_model,
            cust_feat=cust_feat,
            prod_feat=prod_feat,
        )
        fbt = models_mod.association_rules_fbt(txn)
        segment_key = pack.popularity_segment_key(dataframes["customers"])
        popularity = models_mod.popularity_ranking(txn, dataframes["customers"], segment_key)

        store.write_personalized(run_id, personalized)
        store.write_fbt(run_id, fbt)
        store.write_popularity(run_id, popularity)
        store.mark_run_completed(run_id, eda_summary)
    except ValidationError as e:
        store.mark_run_failed(run_id, str(e))
    except Exception as e:  # surfaced via GET /pipeline/status, not swallowed
        store.mark_run_failed(run_id, f"{type(e).__name__}: {e}")
