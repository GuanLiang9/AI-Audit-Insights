import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const SEVERITY_COLORS = { High: "#ef4444", Medium: "#f59e0b", Low: "#10b981" };
const BAR = "#10b981";
const PIE = ["#10b981", "#06b6d4", "#6366f1", "#f59e0b", "#ef4444", "#a78bfa", "#ec4899", "#14b8a6"];

function Card({ title, children, className = "" }) {
  return (
    <div className={`rounded-xl border border-neutral-800 bg-neutral-900/60 p-5 ${className}`}>
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-neutral-400">
        {title}
      </h3>
      {children}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/60 px-4 py-2">
      <div className="text-2xl font-bold text-emerald-400">{value}</div>
      <div className="text-xs text-neutral-500">{label}</div>
    </div>
  );
}

const tooltipStyle = {
  contentStyle: { background: "#0a0a0a", border: "1px solid #262626", borderRadius: 8 },
  labelStyle: { color: "#e5e5e5" },
};

export default function InsightsDashboard({ insights, summary, busy, error, onBuild }) {
  const hasData = insights && insights.total_findings > 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex gap-3">
          <Stat label="Reports" value={insights?.total_reports ?? 0} />
          <Stat label="Findings" value={insights?.total_findings ?? 0} />
          <Stat label="Recurring themes" value={insights?.recurring_themes?.length ?? 0} />
        </div>
        <button
          onClick={onBuild}
          disabled={busy}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-40"
        >
          {busy ? "Analysing all reports…" : hasData ? "Rebuild insights" : "Generate insights"}
        </button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {!hasData && !busy && (
        <Card title="No insights yet">
          <p className="text-sm text-neutral-400">
            Upload reports, then click <span className="text-emerald-400">Generate insights</span> to
            extract structured findings from every report and aggregate them across the corpus.
          </p>
        </Card>
      )}

      {hasData && (
        <>
          {summary && (
            <Card title="Executive summary">
              <p className="whitespace-pre-line text-sm leading-relaxed text-neutral-200">
                {summary.executive_summary}
              </p>
              {summary.key_insights?.length > 0 && (
                <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-neutral-300">
                  {summary.key_insights.map((k, i) => (
                    <li key={i}>{k}</li>
                  ))}
                </ul>
              )}
            </Card>
          )}

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card title="Recurring IT control themes">
              <ResponsiveContainer width="100%" height={Math.max(220, insights.themes.length * 34)}>
                <BarChart data={insights.themes} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#737373", fontSize: 12 }} allowDecimals={false} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={150}
                    tick={{ fill: "#a3a3a3", fontSize: 11 }}
                  />
                  <Tooltip {...tooltipStyle} cursor={{ fill: "#ffffff08" }} />
                  <Bar dataKey="count" fill={BAR} radius={[0, 4, 4, 0]} isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Severity mix">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={insights.severities}
                    dataKey="count"
                    nameKey="name"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={2}
                    isAnimationActive={false}
                    label={(e) => `${e.name}: ${e.count}`}
                  >
                    {insights.severities.map((s) => (
                      <Cell key={s.name} fill={SEVERITY_COLORS[s.name] ?? "#737373"} />
                    ))}
                  </Pie>
                  <Tooltip {...tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Technology risk areas">
              <ResponsiveContainer width="100%" height={Math.max(220, insights.risk_areas.length * 34)}>
                <BarChart data={insights.risk_areas} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#737373", fontSize: 12 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={150} tick={{ fill: "#a3a3a3", fontSize: 11 }} />
                  <Tooltip {...tooltipStyle} cursor={{ fill: "#ffffff08" }} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} isAnimationActive={false}>
                    {insights.risk_areas.map((_, i) => (
                      <Cell key={i} fill={PIE[i % PIE.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Most affected agencies / systems">
              <ResponsiveContainer width="100%" height={Math.max(220, insights.agencies.length * 28)}>
                <BarChart data={insights.agencies} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <XAxis type="number" tick={{ fill: "#737373", fontSize: 12 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#a3a3a3", fontSize: 10 }} />
                  <Tooltip {...tooltipStyle} cursor={{ fill: "#ffffff08" }} />
                  <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
