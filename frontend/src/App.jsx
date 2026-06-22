import { useState } from "react";
import UploadForm from "./components/UploadForm";
import StatusPanel from "./components/StatusPanel";
import RecommendationsExplorer from "./components/RecommendationsExplorer";
import EdaPage from "./components/EdaPage";

function App() {
  const [runId, setRunId] = useState(null);
  const [view, setView] = useState("home");

  if (view === "eda") {
    return <EdaPage runId={runId} onBack={() => setView("home")} />;
  }

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-sky-100/80 bg-white/70 backdrop-blur px-6 py-4 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-lg font-semibold">Recommendation Accelerator</h1>
          <p className="text-sm text-slate-500">Upload data, run the pipeline, explore results.</p>
        </div>
        <button
          onClick={() => setView("eda")}
          className="text-sm px-3 py-1.5 rounded-md bg-sky-600 text-white hover:bg-sky-500 shadow-sm"
        >
          View EDA
        </button>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 space-y-3">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">1. Run pipeline</h2>
          <UploadForm onRunStarted={setRunId} />
        </section>

        <section className="lg:col-span-1 space-y-3">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">2. Run status</h2>
          <StatusPanel runId={runId} onViewEda={() => setView("eda")} />
        </section>

        <section className="lg:col-span-1 space-y-3">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide">3. Explore recommendations</h2>
          <RecommendationsExplorer runId={runId} />
        </section>
      </main>
    </div>
  );
}

export default App;
