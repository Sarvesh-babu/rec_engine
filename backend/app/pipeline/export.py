"""Optional secondary output: a formatted dump of the same result-store
tables an API consumer would otherwise fetch via /recommendations/*.
"""
import pandas as pd

from app.config import RUNS_DIR
from app.pipeline import store


def write_excel_export(run_id: str) -> str:
    tables = store.all_tables_for_export(run_id)
    out_path = RUNS_DIR / run_id / "export.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet_name, rows in tables.items():
            df = pd.DataFrame(rows)
            if not df.empty and "recommendations" in df.columns:
                df["recommendations"] = df["recommendations"].apply(lambda r: ", ".join(r))
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return str(out_path)
