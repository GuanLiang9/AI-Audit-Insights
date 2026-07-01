import { useEffect, useState } from "react";
import {
  analyzeReport,
  buildInsights,
  getExecutiveSummary,
  getInsights,
  getReports,
} from "./api";
import AnalysisView from "./components/AnalysisView";
import InsightsDashboard from "./components/InsightsDashboard";
import QAChat from "./components/QAChat";
import ReportList from "./components/ReportList";
import UploadPanel from "./components/UploadPanel";

const TABS = ["Reports", "Insights", "Q&A"];

export default function App() {
  const [tab, setTab] = useState("Reports");

  // Reports tab state
  const [reports, setReports] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [analyses, setAnalyses] = useState({});
  const [analyzeBusy, setAnalyzeBusy] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");

  // Insights tab state
  const [insights, setInsights] = useState(null);
  const [summary, setSummary] = useState(null);
  const [insightsBusy, setInsightsBusy] = useState(false);
  const [insightsError, setInsightsError] = useState("");

  useEffect(() => {
    getReports().then(setReports).catch(() => {});
    getInsights().then(setInsights).catch(() => {});
  }, []);

  const refreshReports = async () => setReports(await getReports());

  function handleUploaded(result) {
    refreshReports();
    setSelectedId(result.report_id);
  }

  async function handleAnalyze() {
    if (!selectedId) return;
    setAnalyzeBusy(true);
    setAnalyzeError("");
    try {
      const result = await analyzeReport(selectedId);
      setAnalyses((prev) => ({ ...prev, [selectedId]: result }));
      refreshReports();
    } catch (e) {
      setAnalyzeError(e.message);
    } finally {
      setAnalyzeBusy(false);
    }
  }

  async function handleBuildInsights() {
    setInsightsBusy(true);
    setInsightsError("");
    try {
      const res = await buildInsights();
      setInsights(res.insights);
      setSummary(await getExecutiveSummary());
    } catch (e) {
      setInsightsError(e.message);
    } finally {
      setInsightsBusy(false);
    }
  }

  const selectedReport = reports.find((r) => r.id === selectedId) ?? null;

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-8 flex items-center gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 text-lg font-bold text-neutral-950 shadow-lg shadow-emerald-500/20">
          AI
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            AI Audit Insights
          </h1>
          <p className="text-sm text-neutral-500">
            Cross-report analysis of government audit reports
          </p>
        </div>
      </header>

      <nav className="mb-8 inline-flex gap-1 rounded-xl border border-neutral-800 bg-neutral-900/60 p-1 backdrop-blur">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-5 py-2 text-sm font-medium transition ${
              tab === t
                ? "bg-emerald-600 text-white shadow-sm shadow-emerald-500/30"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            {t}
          </button>
        ))}
      </nav>

      {tab === "Reports" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[20rem_1fr]">
          <div className="space-y-6">
            <UploadPanel onUploaded={handleUploaded} />
            <ReportList reports={reports} selectedId={selectedId} onSelect={setSelectedId} />
          </div>
          <AnalysisView
            report={selectedReport}
            analysis={selectedId ? analyses[selectedId] : null}
            busy={analyzeBusy}
            error={analyzeError}
            onAnalyze={handleAnalyze}
          />
        </div>
      )}

      {tab === "Insights" && (
        <InsightsDashboard
          insights={insights}
          summary={summary}
          busy={insightsBusy}
          error={insightsError}
          onBuild={handleBuildInsights}
        />
      )}

      {tab === "Q&A" && <QAChat />}
    </div>
  );
}
