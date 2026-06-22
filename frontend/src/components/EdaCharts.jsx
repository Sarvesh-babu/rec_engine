import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = ["#0ea5e9", "#6366f1", "#22d3ee", "#34d399", "#f59e0b", "#f87171", "#f472b6", "#818cf8"];

export default function EdaCharts({ eda }) {
  return (
    <>
      <SummaryStats eda={eda} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Top products by transaction count">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={eda.top_products || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
              <XAxis dataKey="product_id" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
              <Bar dataKey="count" fill="#0284c7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Transactions over time">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={eda.transactions_over_time || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
              <XAxis dataKey="period" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
              <Line type="monotone" dataKey="count" stroke="#06b6d4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Price distribution">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={eda.price_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
              <XAxis
                dataKey="range"
                stroke="#64748b"
                tick={{ fontSize: 9 }}
                angle={-30}
                textAnchor="end"
                height={50}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
              <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Basket size distribution">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={eda.basket_size_distribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
              <XAxis dataKey="basket_size" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
              <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {eda.category_breakdown && (
          <ChartCard title="Transactions by category">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={eda.category_breakdown}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ category }) => category}
                >
                  {eda.category_breakdown.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        )}

        {eda.segment_breakdown && (
          <ChartCard title="Transactions by customer segment">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={eda.segment_breakdown}
                  dataKey="count"
                  nameKey="segment"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ segment }) => segment}
                >
                  {eda.segment_breakdown.map((_, i) => (
                    <Cell key={i} fill={COLORS[(i + 3) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #dbeafe" }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        )}
      </div>

      {eda.warnings?.length > 0 && (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-3">
          <p className="text-xs font-semibold text-amber-700 mb-1">Warnings</p>
          <ul className="text-xs text-amber-700 list-disc list-inside">
            {eda.warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="rounded-md border border-sky-100 bg-white/80 p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700 mb-2">{title}</h3>
      {children}
    </div>
  );
}

function SummaryStats({ eda }) {
  const stats = [
    ["Transactions", eda.n_transactions],
    ["Customers", eda.n_customers],
    ["Products", eda.n_products],
    ["Date span (days)", eda.date_span_days],
    ["Avg txns / customer", eda.avg_transactions_per_customer?.toFixed(2)],
    ["Avg quantity", eda.avg_quantity?.toFixed(2)],
    ["Avg price", eda.avg_price?.toFixed(2)],
    ["Sparsity", eda.sparsity?.toFixed(3)],
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {stats.map(([label, value]) => (
        <div key={label} className="rounded-md border border-sky-100 bg-white/80 p-3 shadow-sm">
          <p className="text-xs text-slate-500">{label}</p>
          <p className="text-lg font-semibold text-slate-900">{String(value)}</p>
        </div>
      ))}
    </div>
  );
}
