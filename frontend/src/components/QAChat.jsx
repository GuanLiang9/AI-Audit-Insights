import { useState } from "react";
import { askQuestion } from "../api";

const SUGGESTIONS = [
  "What were the most common IT access control weaknesses?",
  "Which agencies had procurement lapses?",
  "Summarise the data protection findings across all reports.",
];

export default function QAChat() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function ask(q) {
    const query = (q ?? question).trim();
    if (!query) return;
    setQuestion(query);
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await askQuestion(query));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-5">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-400">
          Ask the reports
        </h3>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder="Ask a question about the uploaded audit reports…"
            className="flex-1 rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-emerald-600"
          />
          <button
            onClick={() => ask()}
            disabled={busy}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-40"
          >
            {busy ? "Thinking…" : "Ask"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => ask(s)}
              disabled={busy}
              className="rounded-full border border-neutral-800 px-3 py-1 text-xs text-neutral-400 transition hover:border-neutral-600 hover:text-neutral-200 disabled:opacity-40"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {result && (
        <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-5">
          <p className="whitespace-pre-line text-sm leading-relaxed text-neutral-100">
            {result.answer.replace(/\*\*/g, "")}
          </p>
          {result.sources?.length > 0 && (
            <div className="mt-4 border-t border-neutral-800 pt-3">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Sources
              </p>
              <ul className="space-y-1 text-xs text-neutral-400">
                {result.sources.map((s) => (
                  <li key={s.id}>
                    <span className="text-emerald-400">[{s.id}]</span> {s.filename} · chunk{" "}
                    {s.chunk_index}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
