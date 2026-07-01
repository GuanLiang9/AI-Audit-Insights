function Section({ title, items }) {
  if (!items?.length) return null;
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-400">
        {title}
      </h3>
      <ul className="list-disc space-y-1 pl-5 text-sm text-neutral-200">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function AnalysisView({ report, analysis, busy, error, onAnalyze }) {
  if (!report) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-neutral-800 bg-neutral-900/60 p-10 text-neutral-500">
        Select a report to view its analysis.
      </div>
    );
  }

  return (
    <div className="space-y-6 rounded-xl border border-neutral-800 bg-neutral-900/60 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{report.filename}</h2>
          <p className="text-xs text-neutral-500">
            {report.pages} pages · {report.chunks} chunks
          </p>
        </div>
        <button
          onClick={onAnalyze}
          disabled={busy}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-40"
        >
          {busy ? "Analysing…" : analysis ? "Re-analyse" : "Analyse"}
        </button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {analysis ? (
        <div className="space-y-6">
          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-neutral-400">
              Executive summary
            </h3>
            <p className="text-sm leading-relaxed text-neutral-200">{analysis.summary}</p>
          </div>
          <Section title="Key observations" items={analysis.key_observations} />
          <Section title="Risk areas" items={analysis.risk_areas} />
        </div>
      ) : (
        !busy && (
          <p className="text-sm text-neutral-500">
            Not analysed yet — click “Analyse” to run the AI pass.
          </p>
        )
      )}
    </div>
  );
}
