import shutil
import uuid

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import OPTIONAL_FILES, REQUIRED_FILES, RUNS_DIR, TOP_K_DEFAULT
from app.pipeline import store
from app.pipeline.export import write_excel_export
from app.pipeline.runner import run_pipeline
from app.registry import available_industries

app = FastAPI(title="Recommendation Accelerator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
store.init_db()


@app.get("/industries")
def list_industries():
    return {"industries": available_industries()}


@app.post("/pipeline/run")
async def start_pipeline_run(
    background_tasks: BackgroundTasks,
    industry: str,
    transactions: UploadFile = File(...),
    customers: UploadFile = File(...),
    products: UploadFile = File(...),
    sessions: UploadFile | None = File(None),
    returns: UploadFile | None = File(None),
    search_logs: UploadFile | None = File(None),
    promotions: UploadFile | None = File(None),
):
    run_id = uuid.uuid4().hex[:12]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    uploads = {
        "transactions": transactions,
        "customers": customers,
        "products": products,
        "sessions": sessions,
        "returns": returns,
        "search_logs": search_logs,
        "promotions": promotions,
    }
    file_paths: dict[str, str] = {}
    for name, upload in uploads.items():
        if upload is None:
            continue
        dest = run_dir / f"{name}.csv"
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)
        file_paths[name] = str(dest)

    background_tasks.add_task(run_pipeline, run_id, industry, file_paths)
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Unknown run_id '{run_id}'")
    return run


def _resolve_run_id(run_id: str | None) -> str:
    if run_id:
        return run_id
    latest = store.latest_completed_run()
    if not latest:
        raise HTTPException(404, "No completed pipeline run yet")
    return latest["run_id"]


@app.get("/pipeline/eda")
def get_eda(run_id: str | None = None):
    rid = _resolve_run_id(run_id)
    run = store.get_run(rid)
    if not run or not run.get("eda"):
        raise HTTPException(404, f"No EDA available for run '{rid}'")
    return {"run_id": rid, "computed_at": run["computed_at"], **run["eda"]}


@app.get("/recommendations/personalized/{customer_id}")
def get_personalized(customer_id: str, run_id: str | None = None):
    rid = _resolve_run_id(run_id)
    run = store.get_run(rid)
    items = store.get_personalized(rid, customer_id)
    if items is None:
        items = store.get_popularity(rid, "overall") or []
        source = "popularity_fallback"
    else:
        source = "personalized"
    return {
        "customer_id": customer_id,
        "run_id": rid,
        "computed_at": run["computed_at"] if run else None,
        "source": source,
        "recommendations": items[:TOP_K_DEFAULT],
    }


@app.get("/recommendations/frequently-bought-together/{product_id}")
def get_fbt(product_id: str, run_id: str | None = None):
    rid = _resolve_run_id(run_id)
    run = store.get_run(rid)
    items = store.get_fbt(rid, product_id) or []
    return {
        "product_id": product_id,
        "run_id": rid,
        "computed_at": run["computed_at"] if run else None,
        "recommendations": items[:TOP_K_DEFAULT],
    }


@app.get("/recommendations/popular")
def get_popular(segment: str | None = None, run_id: str | None = None):
    rid = _resolve_run_id(run_id)
    run = store.get_run(rid)
    key = f"segment:{segment}" if segment else "overall"
    items = store.get_popularity(rid, key)
    if items is None:
        items = store.get_popularity(rid, "overall") or []
    return {
        "segment": segment or "overall",
        "run_id": rid,
        "computed_at": run["computed_at"] if run else None,
        "recommendations": items[:TOP_K_DEFAULT],
    }


@app.get("/export/excel/{run_id}")
def export_excel(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(404, f"Unknown run_id '{run_id}'")
    if run["status"] != "completed":
        raise HTTPException(409, f"Run '{run_id}' is not completed (status={run['status']})")
    path = write_excel_export(run_id)
    return FileResponse(path, filename=f"recommendations_{run_id}.xlsx")


@app.get("/")
def root():
    return {
        "service": "Recommendation Accelerator",
        "required_files": REQUIRED_FILES,
        "optional_files": OPTIONAL_FILES,
    }
