import { useState } from "react";
import { uploadPdf } from "../api";

export default function UploadPanel({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const result = await uploadPdf(file);
      setFile(null);
      onUploaded(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-5">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-400">
        Upload audit report
      </h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files[0] ?? null)}
        className="block w-full text-sm text-neutral-300 file:mr-3 file:rounded-lg file:border-0 file:bg-emerald-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-emerald-500"
      />
      <button
        onClick={handleUpload}
        disabled={!file || busy}
        className="mt-4 w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {busy ? "Processing…" : "Upload & index"}
      </button>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
    </div>
  );
}
