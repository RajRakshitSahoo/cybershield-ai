import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Search, Trash2, Download, Bookmark, ExternalLink, X } from "lucide-react";
import { getHistory, deleteHistoryItem, bookmarkItem, api } from "../lib/api";
import type { AnalysisReport } from "../lib/api";
import StatusPill from "../components/StatusPill";
import ReportView from "../components/ReportView";

type ScanRow = AnalysisReport & { id: string };

export default function History() {
  const [items, setItems] = useState<ScanRow[]>([]);
  const [search, setSearch] = useState("");
  const [verdict, setVerdict] = useState("");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<ScanRow | null>(null);

  const load = async () => {
    setLoading(true);
    const data = await getHistory(search, verdict);
    setItems(data);
    setLoading(false);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [verdict]);

  const handleDelete = async (id: string) => {
    await deleteHistoryItem(id);
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const handleExportPdf = async (id: string) => {
    const res = await api.get(`/report/${id}/pdf`, { responseType: "blob" });
    const blob = new Blob([res.data], { type: "application/pdf" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `cybershield-report-${id}.pdf`;
    link.click();
  };

  if (selected) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-10">
        <button onClick={() => setSelected(null)} className="mb-6 flex items-center gap-1.5 text-xs text-ink-dim hover:text-ink">
          <X size={14} /> Close report
        </button>
        <ReportView report={selected} onExportPdf={() => handleExportPdf(selected.id)} onBookmark={() => bookmarkItem(selected.id)} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <h1 className="font-display text-2xl font-semibold text-ink">Scan History</h1>
      <p className="mt-1 text-sm text-ink-dim">Every scan you've run while signed in.</p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load()}
            placeholder="Search by URL…"
            className="w-full rounded-lg border border-line bg-panel py-2.5 pl-9 pr-3 text-sm text-ink placeholder:text-ink-faint focus:border-signal/50 focus:outline-none"
          />
        </div>
        <select
          value={verdict}
          onChange={(e) => setVerdict(e.target.value)}
          className="rounded-lg border border-line bg-panel px-3 py-2.5 text-sm text-ink focus:border-signal/50 focus:outline-none"
        >
          <option value="">All verdicts</option>
          <option value="Safe">Safe</option>
          <option value="Suspicious">Suspicious</option>
          <option value="Phishing">Phishing</option>
        </select>
      </div>

      <div className="mt-6 space-y-3">
        {loading && <p className="text-xs text-ink-faint">Loading…</p>}
        {!loading && items.length === 0 && (
          <div className="panel rounded-xl p-8 text-center text-sm text-ink-faint">No scans yet. Run one from the homepage.</div>
        )}
        {items.map((item, i) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            className="panel flex flex-col gap-3 rounded-xl p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <button onClick={() => setSelected(item)} className="flex flex-1 items-center gap-3 text-left">
              <StatusPill status={item.ai_prediction.verdict} />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-ink">{item.url}</p>
                <p className="text-[11px] text-ink-faint">{new Date(item.scanned_at).toLocaleString()} &middot; risk {item.ai_prediction.risk_score}/100</p>
              </div>
            </button>
            <div className="flex items-center gap-1.5">
              <button onClick={() => bookmarkItem(item.id)} className="rounded-md p-2 text-ink-faint hover:bg-void hover:text-signal" title="Bookmark">
                <Bookmark size={14} />
              </button>
              <button onClick={() => handleExportPdf(item.id)} className="rounded-md p-2 text-ink-faint hover:bg-void hover:text-signal" title="Export PDF">
                <Download size={14} />
              </button>
              <a href={item.url} target="_blank" rel="noreferrer" className="rounded-md p-2 text-ink-faint hover:bg-void hover:text-signal" title="Visit">
                <ExternalLink size={14} />
              </a>
              <button onClick={() => handleDelete(item.id)} className="rounded-md p-2 text-ink-faint hover:bg-void hover:text-alert-critical" title="Delete">
                <Trash2 size={14} />
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
