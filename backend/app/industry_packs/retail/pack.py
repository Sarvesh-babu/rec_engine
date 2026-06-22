"""Retail-specific schema extension and feature gating rules.

Column names, category taxonomy assumptions, and business rules specific
to retail live here and nowhere else in the pipeline.
"""
import pandas as pd


class RetailPack:
    name = "retail"

    # Columns retail expects on top of the universal schema, if present.
    product_schema_extension = ["category", "brand"]
    customer_schema_extension = ["segment"]

    def validate_extension(self, products: pd.DataFrame, customers: pd.DataFrame) -> list[str]:
        """Soft warnings only -- extension columns are optional enrichments."""
        warnings = []
        for col in self.product_schema_extension:
            if col not in products.columns:
                warnings.append(f"retail pack: products missing optional column '{col}'")
        for col in self.customer_schema_extension:
            if col not in customers.columns:
                warnings.append(f"retail pack: customers missing optional column '{col}'")
        return warnings

    def popularity_segment_key(self, customers: pd.DataFrame) -> str | None:
        """Which customer attribute to segment the popularity fallback by, if any."""
        if "segment" in customers.columns:
            return "segment"
        return None

    def category_key(self, products: pd.DataFrame) -> str | None:
        if "category" in products.columns:
            return "category"
        return None
