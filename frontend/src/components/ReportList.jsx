export default function ReportList({ reports, selectedId, onSelect }) {
  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-5">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-400">
        Reports ({reports.length})
      </h2>

      {reports.length === 0 ? (
        <p className="text-sm text-neutral-500">No reports yet. Upload a PDF to start.</p>
      ) : (
        <ul className="space-y-2">
          {reports.map((r) => (
            <li key={r.id}>
              <button
                onClick={() => onSelect(r.id)}
                className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition ${
                  r.id === selectedId
                    ? "border-emerald-500/60 bg-emerald-500/10"
                    : "border-neutral-800 hover:border-neutral-700 hover:bg-neutral-800/40"
                }`}
              >
                <span className="block truncate font-medium">{r.filename}</span>
                <span className="text-xs text-neutral-500">
                  {r.pages} pages · {r.chunks} chunks
                  {r.analyzed ? " · analysed" : ""}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
