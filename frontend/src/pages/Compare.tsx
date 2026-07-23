import { useState } from "react";
import { motion } from "framer-motion";
import { GitCompare, Loader2, ArrowRight } from "lucide-react";
import { compareUrls } from "../lib/api";
import StatusPill from "../components/StatusPill";
import RiskGauge from "../components/RiskGauge";

function CompareRow({ label, a, b, saferKey }: { label: string; a: any; b: any; saferKey?: "a" | "b" | "tie" | null }) {
  return (
    <div className="grid grid-cols-3 items-center gap-4 border-b border-line/50 py-3 last:border-0">
      <div className={`text-right text-sm ${saferKey === "a" ? "text-signal font-semibold" : "text-ink-dim"}`}>{String(a ?? "—")}</div>
      <div className="text-center text-[11px] uppercase tracking-wide text-ink-faint">{label}</div>
      <div className={`text-left text-sm ${saferKey === "b" ? "text-signal font-semibold" : "text-ink-dim"}`}>{String(b ?? "—")}</div>
    </div>
  );
}

export default function Compare() {
  const [urlA, setUrlA] = useState("");
  const [urlB, setUrlB] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const handleCompare = async () => {
    if (!urlA.trim() || !urlB.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await compareUrls(urlA.trim(), urlB.trim());
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Comparison failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="flex items-center gap-2">
        <GitCompare size={18} className="text-signal" />
        <h1 className="font-display text-2xl font-semibold text-ink">Compare two websites</h1>
      </div>
      <p className="mt-1 text-sm text-ink-dim">e.g. google.com vs a suspicious lookalike domain.</p>

      <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row">
        <input
          value={urlA} onChange={(e) => setUrlA(e.target.value)} placeholder="google.com"
          className="w-full flex-1 rounded-lg border border-line bg-panel px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-signal/50 focus:outline-none"
        />
        <span className="text-xs font-semibold text-ink-faint">VS</span>
        <input
          value={urlB} onChange={(e) => setUrlB(e.target.value)} placeholder="google-login.xyz"
          className="w-full flex-1 rounded-lg border border-line bg-panel px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-signal/50 focus:outline-none"
        />
        <button
          onClick={handleCompare} disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-signal px-5 py-2.5 text-sm font-semibold text-void shadow-glow transition-transform hover:scale-[1.02] disabled:opacity-60"
        >
          {loading ? <Loader2 size={15} className="animate-spin" /> : <ArrowRight size={15} />}
          Compare
        </button>
      </div>
      {error && <p className="mt-3 text-xs text-alert-critical">{error}</p>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-10 space-y-6">
          <div className="panel flex flex-col items-center justify-around gap-6 rounded-xl p-6 sm:flex-row">
            <div className="text-center">
              <p className="mb-2 truncate text-xs text-ink-dim">{result.report_a.url}</p>
              <RiskGauge score={result.report_a.ai_prediction.risk_score} verdict={result.report_a.ai_prediction.verdict} size={140} />
            </div>
            <div className="text-center">
              <p className="text-[11px] uppercase tracking-wide text-ink-faint">Overall safer</p>
              <p className="mt-1 font-display text-lg font-bold text-signal">
                {result.overall_safer === "a" ? "Site A" : "Site B"}
              </p>
            </div>
            <div className="text-center">
              <p className="mb-2 truncate text-xs text-ink-dim">{result.report_b.url}</p>
              <RiskGauge score={result.report_b.ai_prediction.risk_score} verdict={result.report_b.ai_prediction.verdict} size={140} />
            </div>
          </div>

          <div className="panel rounded-xl p-6">
            <div className="mb-3 grid grid-cols-3 text-center text-[11px] font-semibold uppercase tracking-wide text-ink-faint">
              <span>Site A</span><span>Signal</span><span>Site B</span>
            </div>
            <CompareRow label="Verdict" a={result.comparison.verdict.a} b={result.comparison.verdict.b} />
            <CompareRow label="Domain Age (days)" a={result.comparison.domain_age_days.a} b={result.comparison.domain_age_days.b} saferKey={result.comparison.domain_age_days.safer} />
            <CompareRow label="HTTPS" a={String(result.comparison.https.a)} b={String(result.comparison.https.b)} />
            <CompareRow label="Hosting Country" a={result.comparison.hosting_country.a} b={result.comparison.hosting_country.b} />
            <CompareRow label="Hosting Provider" a={result.comparison.hosting_provider.a} b={result.comparison.hosting_provider.b} />
            <CompareRow label="AI Risk Score" a={result.comparison.ai_risk_score.a} b={result.comparison.ai_risk_score.b} saferKey={result.comparison.ai_risk_score.safer} />
            <CompareRow label="Blacklisted" a={String(result.comparison.blacklisted.a)} b={String(result.comparison.blacklisted.b)} />
            <CompareRow label="Missing Headers" a={result.comparison.missing_security_headers.a} b={result.comparison.missing_security_headers.b} />
          </div>
        </motion.div>
      )}
    </div>
  );
}
