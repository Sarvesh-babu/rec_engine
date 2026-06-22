import { useNavigate } from "react-router-dom";
import UploadForm from "../components/UploadForm";

export default function UploadPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-sky-100/80 bg-white/70 backdrop-blur px-6 py-4 shadow-sm">
        <h1 className="text-lg font-semibold">Recommendation Accelerator</h1>
        <p className="text-sm text-slate-500">Upload your data to get started.</p>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-10">
        <UploadForm onRunStarted={(runId) => navigate(`/eda/${runId}`)} />
      </main>
    </div>
  );
}
