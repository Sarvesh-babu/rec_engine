import { useEffect, useRef, useState } from "react";
import { getRunStatus, excelExportUrl } from "../api";

export default function StatusPanel({ runId, onViewEda }) {
  const [run, setRun] = useState(null);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  useEffect(() => {
    if (!runId) return;
    setRun(null);
    setError(null);

    async function poll() {
      try {
        const data = await getRunStatus(runId);
        setRun(data);
        if (data.status === "running") {
          pollRef.current = setTimeout(poll, 1500);
        }
      } catch (err) {
        setError(err.message);
      }
    }
    poll();
    return () => clearTimeout(pollRef.current);
  }, [runId]);

  if (!runId) {
    return <p className="text-sm text-slate-500">Start a pipeline run to see its status here.</p>;
  }
  if (error) return <p className="text-sm text-rose-600">{error}</p>;
  if (!run) return <p className="text-sm text-slate-500">Loading...</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <StatusBadge status={run.status} />
        <code className="text-xs text-slate-500">{run.run_id}</code>
      </div>

      {run.status === "failed" && <p className="text-sm text-rose-600">{run.error}</p>}

      {run.status === "completed" && run.eda && (
        <>
          <EdaSummary eda={run.eda} computedAt={run.computed_at} />
          <button
            onClick={onViewEda}
            className="block w-full text-sm rounded-md bg-sky-600 hover:bg-sky-500 text-white px-3 py-2 shadow-sm"
          >
            View full EDA
          </button>
          <a
            href={excelExportUrl(run.run_id)}
            className="inline-block text-sm text-sky-700 hover:text-sky-600 underline"
          >
            Download Excel export
          </a>
        </>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    running: "bg-amber-100 text-amber-800 border border-amber-200",
    completed: "bg-emerald-100 text-emerald-800 border border-emerald-200",
    failed: "bg-rose-100 text-rose-800 border border-rose-200",
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded ${styles[status] || "bg-slate-100 text-slate-700 border border-slate-200"}`}>
      {status}
    </span>
  );
}

function EdaSummary({ eda, computedAt }) {
  const rows = [
    ["Transactions", eda.n_transactions],
    ["Customers", eda.n_customers],
    ["Products", eda.n_products],
    ["Date span (days)", eda.date_span_days],
    ["Avg txns / customer", eda.avg_transactions_per_customer?.toFixed(2)],
    ["Avg quantity", eda.avg_quantity?.toFixed(2)],
    ["Avg price", eda.avg_price?.toFixed(2)],
    ["Sparsity", eda.sparsity?.toFixed(3)],
    ["Optional files used", eda.optional_files_present?.join(", ") || "none"],
  ];
  return (
    <div className="rounded-md border border-sky-100 bg-white/80 p-3 shadow-sm">
      <p className="text-xs text-slate-500 mb-2">Computed at {computedAt}</p>
      <dl className="grid grid-cols-2 gap-y-1 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="contents">
            <dt className="text-slate-500">{label}</dt>
            <dd className="text-slate-900 text-right">{String(value)}</dd>
          </div>
        ))}
      </dl>
      {eda.warnings?.length > 0 && (
        <ul className="mt-2 text-xs text-amber-700 list-disc list-inside">
          {eda.warnings.map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
