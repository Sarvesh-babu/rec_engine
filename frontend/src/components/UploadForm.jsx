import { useEffect, useState } from "react";
import { listIndustries, uploadAndValidate } from "../api";

const REQUIRED_FILES = ["transactions", "customers", "products"];
const OPTIONAL_FILES = ["sessions", "returns", "search_logs", "promotions"];

export default function UploadForm({ onRunStarted }) {
  const [industries, setIndustries] = useState(["retail"]);
  const [industry, setIndustry] = useState("retail");
  const [files, setFiles] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listIndustries()
      .then((data) => {
        setIndustries(data.industries);
        if (data.industries.length) setIndustry(data.industries[0]);
      })
      .catch(() => {});
  }, []);

  const missingRequired = REQUIRED_FILES.filter((f) => !files[f]);

  function handleFileChange(name, fileList) {
    setFiles((prev) => ({ ...prev, [name]: fileList?.[0] ?? null }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const result = await uploadAndValidate(industry, files);
      onRunStarted(result.run_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Industry</label>
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="w-full rounded-md bg-white border border-sky-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
        >
          {industries.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </div>

      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-slate-800 mb-1">Required files</legend>
        {REQUIRED_FILES.map((name) => (
          <FileRow key={name} name={name} required onChange={handleFileChange} file={files[name]} />
        ))}
      </fieldset>

      <fieldset className="space-y-3">
        <legend className="text-sm font-semibold text-slate-800 mb-1">Optional files</legend>
        {OPTIONAL_FILES.map((name) => (
          <FileRow key={name} name={name} onChange={handleFileChange} file={files[name]} />
        ))}
      </fieldset>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      <button
        type="submit"
        disabled={missingRequired.length > 0 || submitting}
        className="w-full rounded-md bg-gradient-to-r from-sky-600 to-cyan-500 hover:from-sky-500 hover:to-cyan-400 text-white disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium transition shadow-sm"
      >
        {submitting ? "Uploading..." : "Upload & validate"}
      </button>
      {missingRequired.length > 0 && (
        <p className="text-xs text-slate-500">Missing required: {missingRequired.join(", ")}</p>
      )}
    </form>
  );
}

function FileRow({ name, required, file, onChange }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-sky-100 bg-white/80 px-3 py-2 shadow-sm">
      <span className="text-sm text-slate-700">
        {name.replace(/_/g, " ")}
        {required && <span className="text-sky-600"> *</span>}
      </span>
      <div className="flex items-center gap-2">
        {file && <span className="text-xs text-slate-500 truncate max-w-[140px]">{file.name}</span>}
        <label className="text-xs px-2 py-1 rounded bg-sky-50 hover:bg-sky-100 text-sky-700 cursor-pointer border border-sky-200">
          Choose
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => onChange(name, e.target.files)}
          />
        </label>
      </div>
    </div>
  );
}
