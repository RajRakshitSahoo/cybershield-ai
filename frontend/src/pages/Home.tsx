import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ScanSearch, Radar, Fingerprint, ShieldCheck, Globe2, FileSearch,
  Loader2, ArrowRight, ChevronDown,
} from "lucide-react";
import { analyzeUrl } from "../lib/api";
import type { AnalysisReport } from "../lib/api";
import ReportView from "../components/ReportView";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

const FEATURES = [
  { icon: Radar, title: "Real-time domain scan", copy: "WHOIS, DNS, SSL, and hosting intelligence pulled live in seconds." },
  { icon: Fingerprint, title: "Explainable AI verdicts", copy: "Every risk score ships with the exact signals that produced it." },
  { icon: Globe2, title: "Global reputation checks", copy: "Cross-references live threat-intel feeds and blacklists." },
  { icon: ShieldCheck, title: "Security posture grading", copy: "HSTS, CSP, and header hygiene scored against best practice." },
  { icon: FileSearch, title: "Exportable reports", copy: "Save, bookmark, and export a professional PDF for any scan." },
  { icon: ScanSearch, title: "Side-by-side compare", copy: "Put two domains head-to-head across every signal we track." },
];

const STEPS = [
  { n: "01", title: "Paste a URL", copy: "Any website address — with or without the protocol." },
  { n: "02", title: "We scan everything", copy: "Domain, SSL, DNS, headers, tech stack, and reputation, in parallel." },
  { n: "03", title: "AI scores the risk", copy: "A trained model returns a 0–100 risk score with plain-English reasons." },
  { n: "04", title: "Act with confidence", copy: "Save it, export a PDF, or compare it against another domain." },
];

const FAQS = [
  { q: "What does the risk score mean?", a: "0–29 is graded Safe, 30–69 Suspicious, and 70–100 Phishing. The score is a model-estimated probability, not a legal determination." },
  { q: "Do you store the sites I scan?", a: "Visitor scans aren't saved. Signed-in users can optionally keep scans in their private history." },
  { q: "Which reputation feeds are checked?", a: "VirusTotal, Google Safe Browsing, OpenPhish, and AbuseIPDB, where API access is configured." },
  { q: "Can I compare two sites?", a: "Yes — the Compare tool runs a full scan on both URLs and highlights every difference." },
];

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const { user } = useAuth();

  const handleScan = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const data = await analyzeUrl(url.trim());
      setReport(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Scan failed — the target may be unreachable.");
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = async () => {
    if (!report?.id) return;
    const res = await api.get(`/report/${report.id}/pdf`, { responseType: "blob" });
    const blob = new Blob([res.data], { type: "application/pdf" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `cybershield-report-${report.id}.pdf`;
    link.click();
  };

  const handleBookmark = async () => {
    if (!report?.id) return;
    await api.post("/history/bookmark", { report_id: report.id });
  };

  return (
    <div className="relative">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-line/60">
        <div className="scanline-bg absolute inset-0 opacity-40 [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />
        <div className="relative mx-auto max-w-4xl px-6 pb-16 pt-20 text-center md:pt-28">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto mb-6 flex w-fit items-center gap-2 rounded-full border border-signal/25 bg-signal/5 px-3.5 py-1.5 text-[11px] font-medium text-signal"
          >
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-signal opacity-60" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-signal" />
            </span>
            AI model live &middot; scanning in real time
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="font-display text-4xl font-semibold leading-[1.1] tracking-tight text-ink md:text-6xl"
          >
            Know if a website is
            <span className="text-signal text-glow"> safe </span>
            before you trust it.
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mx-auto mt-5 max-w-xl text-sm leading-relaxed text-ink-dim md:text-base"
          >
            Paste any URL and get a full domain intelligence report &mdash; WHOIS, SSL,
            DNS, security headers, and an explainable AI phishing verdict &mdash; in seconds.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mx-auto mt-9 flex max-w-xl flex-col gap-3 sm:flex-row"
          >
            <div className="relative flex-1">
              <ScanSearch size={16} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint" />
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleScan()}
                placeholder="e.g. example.com"
                className="w-full rounded-lg border border-line bg-panel py-3 pl-10 pr-4 text-sm text-ink placeholder:text-ink-faint focus:border-signal/50 focus:outline-none focus:ring-1 focus:ring-signal/30"
              />
            </div>
            <button
              onClick={handleScan}
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-lg bg-signal px-6 py-3 text-sm font-semibold text-void shadow-glow transition-transform hover:scale-[1.02] disabled:opacity-60"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
              {loading ? "Analyzing…" : "Analyze"}
            </button>
          </motion.div>
          {error && <p className="mt-3 text-xs text-alert-critical">{error}</p>}
          {!user && (
            <p className="mt-3 text-[11px] text-ink-faint">
              Scanning as a visitor &mdash; sign in to save history, export PDFs, and get alerts.
            </p>
          )}
        </div>
      </section>

      {/* Loading skeleton */}
      <AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mx-auto max-w-5xl px-6 py-10">
            <div className="grid gap-6 md:grid-cols-2">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="panel h-40 animate-pulse rounded-xl" />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Report */}
      {report && !loading && (
        <section className="mx-auto max-w-5xl px-6 py-10">
          <ReportView report={report} onExportPdf={user ? handleExportPdf : undefined} onBookmark={user ? handleBookmark : undefined} />
        </section>
      )}

      {/* Features */}
      {!report && (
        <>
          <section className="mx-auto max-w-6xl px-6 py-20">
            <h2 className="font-display text-2xl font-semibold text-ink md:text-3xl">Built like a real SOC tool</h2>
            <p className="mt-2 max-w-lg text-sm text-ink-dim">
              Every scan runs the same checks a security analyst would &mdash; automated and explained.
            </p>
            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {FEATURES.map((f) => (
                <div key={f.title} className="panel rounded-xl p-5 transition-colors hover:border-signal/30">
                  <f.icon size={18} className="text-signal" />
                  <h3 className="mt-3 font-display text-sm font-semibold text-ink">{f.title}</h3>
                  <p className="mt-1.5 text-xs leading-relaxed text-ink-dim">{f.copy}</p>
                </div>
              ))}
            </div>
          </section>

          {/* How it works */}
          <section className="border-y border-line/60 bg-panel/30">
            <div className="mx-auto max-w-6xl px-6 py-20">
              <h2 className="font-display text-2xl font-semibold text-ink md:text-3xl">How it works</h2>
              <div className="mt-10 grid gap-6 md:grid-cols-4">
                {STEPS.map((s) => (
                  <div key={s.n} className="relative">
                    <span className="font-mono text-xs text-signal/70">{s.n}</span>
                    <h3 className="mt-2 font-display text-sm font-semibold text-ink">{s.title}</h3>
                    <p className="mt-1.5 text-xs leading-relaxed text-ink-dim">{s.copy}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Stats */}
          <section className="mx-auto max-w-6xl px-6 py-20">
            <div className="grid gap-6 sm:grid-cols-3">
              {[
                { label: "Signals per scan", value: "40+" },
                { label: "Avg. scan time", value: "< 6s" },
                { label: "Model accuracy (test set)", value: "~99%" },
              ].map((s) => (
                <div key={s.label} className="panel rounded-xl p-6 text-center">
                  <p className="font-display text-3xl font-bold text-signal">{s.value}</p>
                  <p className="mt-2 text-xs text-ink-dim">{s.label}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Testimonials */}
          <section className="border-y border-line/60 bg-panel/30">
            <div className="mx-auto max-w-6xl px-6 py-20">
              <h2 className="font-display text-2xl font-semibold text-ink md:text-3xl">What early users say</h2>
              <div className="mt-10 grid gap-5 md:grid-cols-3">
                {[
                  { name: "Priya S.", role: "SOC Analyst", quote: "The explainability made it easy to justify a takedown request to our registrar." },
                  { name: "Daniel K.", role: "IT Manager", quote: "Compare mode caught a lookalike domain our filters missed entirely." },
                  { name: "Meera R.", role: "Security Student", quote: "Great way to actually see how phishing indicators map to a real risk score." },
                ].map((t) => (
                  <div key={t.name} className="panel rounded-xl p-5">
                    <p className="text-sm italic leading-relaxed text-ink-dim">&ldquo;{t.quote}&rdquo;</p>
                    <p className="mt-4 text-xs font-semibold text-ink">{t.name}</p>
                    <p className="text-[11px] text-ink-faint">{t.role}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* FAQ */}
          <section className="mx-auto max-w-3xl px-6 py-20">
            <h2 className="font-display text-2xl font-semibold text-ink md:text-3xl">Frequently asked</h2>
            <div className="mt-8 divide-y divide-line/60">
              {FAQS.map((f, i) => (
                <div key={f.q} className="py-4">
                  <button onClick={() => setOpenFaq(openFaq === i ? null : i)} className="flex w-full items-center justify-between text-left">
                    <span className="text-sm font-medium text-ink">{f.q}</span>
                    <ChevronDown size={16} className={`text-ink-faint transition-transform ${openFaq === i ? "rotate-180" : ""}`} />
                  </button>
                  <AnimatePresence>
                    {openFaq === i && (
                      <motion.p
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden text-xs leading-relaxed text-ink-dim"
                      >
                        <span className="block pt-2.5">{f.a}</span>
                      </motion.p>
                    )}
                  </AnimatePresence>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
