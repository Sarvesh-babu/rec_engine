import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getEda } from "../api";
import { usePipelineStatus } from "../hooks/usePipelineStatus";
import EdaCharts from "../components/EdaCharts";

const EDA_AVAILABLE_STATUSES = ["eda_ready", "training", "completed"];

export default function EdaReviewPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const { run, error: statusError } = usePipelineStatus(runId);
  const [eda, setEda] = useState(null);
  const [edaError, setEdaError] = useState(null);

  useEffect(() => {
    if (run && EDA_AVAILABLE_STATUSES.includes(run.status)) {
      getEda(runId)
        .then(setEda)
        .catch((err) => setEdaError(err.message));
    }
  }, [run, runId]);

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-sky-100/80 bg-white/70 backdrop-blur px-6 py-4 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-lg font-semibold">Review your data</h1>
          <p className="text-sm text-slate-500">Check the EDA below, then choose your models.</p>
        </div>
        <code className="text-xs text-slate-400">{runId}</code>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {statusError && <p className="text-sm text-rose-600">{statusError}</p>}
        {run?.status === "validating" && <p className="text-sm text-slate-500">Validating upload...</p>}
        {run?.status === "failed" && <p className="text-sm text-rose-600">{run.error}</p>}

        {edaError && <p className="text-sm text-rose-600">{edaError}</p>}
        {eda && <EdaCharts eda={eda} />}

        {run?.status === "eda_ready" && eda && (
          <div className="rounded-md border border-sky-200 bg-white/80 p-4 shadow-sm flex items-center justify-between gap-4">
            <p className="text-sm text-slate-600">Data looks good? Choose your models next.</p>
            <button
              onClick={() => navigate(`/models/${runId}`)}
              className="rounded-md bg-gradient-to-r from-sky-600 to-cyan-500 hover:from-sky-500 hover:to-cyan-400 text-white px-4 py-2 text-sm font-medium shadow-sm whitespace-nowrap"
            >
              Continue to model settings
            </button>
          </div>
        )}

        {(run?.status === "training" || run?.status === "completed") && (
          <p className="text-sm text-slate-500">
            Training already started for this run.{" "}
            <button onClick={() => navigate(`/results/${runId}`)} className="text-sky-600 underline">
              Go to results
            </button>
          </p>
        )}
      </main>
    </div>
  );
}
