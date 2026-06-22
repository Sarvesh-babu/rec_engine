import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getMetrics } from "../api";

const METRIC_LABELS = { precision: "Precision", recall: "Recall", hit_rate: "Hit rate" };

export default function ValidationPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getMetrics(runId)
      .then(setMetrics)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [runId]);

  const chartData =
    metrics?.top_k_values.flatMap((k) =>
      Object.keys(METRIC_LABELS).map((m) => ({
        metric: `${METRIC_LABELS[m]}@${k}`,
        Model: metrics.model[`${m}_at_${k}`],
        "Popularity baseline": metrics.popularity_baseline[`${m}_at_${k}`],
      }))
    ) ?? [];

  return (
    <div className="min-h-screen text-slate-900">
      <header className="border-b border-sky-100/80 bg-white/70 backdrop-blur px-6 py-4 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-lg font-semibold">Model validation</h1>
          <p className="text-sm text-slate-500">Offline evaluation via temporal leave-out.</p>
        </div>
        <button
          onClick={() => navigate(`/results/${runId}`)}
          className="text-sm px-3 py-1.5 rounded-md bg-sky-600 text-white hover:bg-sky-500 shadow-sm"
        >
          Back to results
        </button>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {loading && <p className="text-sm text-slate-500">Loading metrics...</p>}
        {error && <p className="text-sm text-rose-600">{error}</p>}

        {metrics && (
          <>
            <p className="text-sm text-slate-500">
              Evaluated on {metrics.n_customers_evaluated} customers by holding out their most recent purchases
              and checking whether the model recommends them back.
            </p>

            <div className="rounded-md border border-sky-100 bg-white/80 p-4 shadow-sm">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
                  <XAxis dataKey="metric" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="Model" fill="#0284c7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Popularity baseline" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <MetricsTable metrics={metrics} />
          </>
        )}
      </main>
    </div>
  );
}

function MetricsTable({ metrics }) {
  return (
    <div className="rounded-md border border-sky-100 bg-white/80 p-4 shadow-sm overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500">
            <th className="py-1 pr-4">Metric</th>
            <th className="py-1 pr-4">Model</th>
            <th className="py-1">Popularity baseline</th>
          </tr>
        </thead>
        <tbody>
          {metrics.top_k_values.flatMap((k) =>
            Object.keys(METRIC_LABELS).map((m) => (
              <tr key={`${m}_${k}`} className="border-t border-slate-100">
                <td className="py-1 pr-4 text-slate-700">
                  {METRIC_LABELS[m]}@{k}
                </td>
                <td className="py-1 pr-4 font-medium text-slate-900">
                  {metrics.model[`${m}_at_${k}`]?.toFixed(3)}
                </td>
                <td className="py-1 text-slate-600">{metrics.popularity_baseline[`${m}_at_${k}`]?.toFixed(3)}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
