import { useNavigate, useParams } from "react-router-dom";
import { usePipelineStatus } from "../hooks/usePipelineStatus";
import { excelExportUrl } from "../api";
import RecommendationsExplorer from "../components/RecommendationsExplorer";

export default function ResultsPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const { run, error } = usePipelineStatus(runId);

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-sky-100/80 bg-white/70 backdrop-blur px-6 py-4 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-lg font-semibold">Results</h1>
          <p className="text-sm text-slate-500">Explore recommendations from this run.</p>
        </div>
        <div className="flex items-center gap-3">
          <code className="text-xs text-slate-400">{runId}</code>
          <button
            onClick={() => navigate("/upload")}
            className="text-sm px-3 py-1.5 rounded-md bg-sky-600 text-white hover:bg-sky-500 shadow-sm"
          >
            New run
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {error && <p className="text-sm text-rose-600">{error}</p>}
        {run?.status === "training" && (
          <p className="text-sm text-slate-500">Training models, this can take a moment...</p>
        )}
        {run?.status === "failed" && <p className="text-sm text-rose-600">{run.error}</p>}

        {run?.status === "completed" && (
          <>
            <div className="flex items-center gap-4">
              <a
                href={excelExportUrl(runId)}
                className="text-sm text-sky-700 hover:text-sky-600 underline"
              >
                Download Excel export
              </a>
              <button
                onClick={() => navigate(`/validation/${runId}`)}
                className="text-sm text-sky-700 hover:text-sky-600 underline"
              >
                View model validation metrics
              </button>
            </div>
            <RecommendationsExplorer runId={runId} />
          </>
        )}
      </main>
    </div>
  );
}
