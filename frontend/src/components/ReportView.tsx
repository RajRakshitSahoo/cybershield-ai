import { motion } from "framer-motion";
import {
  Globe, Lock, Server, Fingerprint, ShieldAlert, Clock, Download, Bookmark,
} from "lucide-react";
import Panel from "./Panel";
import RiskGauge from "./RiskGauge";
import StatusPill from "./StatusPill";
import type { AnalysisReport } from "../lib/api";

function Row({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="flex items-center justify-between border-b border-line/50 py-2 last:border-0">
      <span className="text-xs text-ink-faint">{label}</span>
      <span className="max-w-[60%] truncate text-right text-xs font-medium text-ink" title={String(value ?? "")}>
        {value ?? "—"}
      </span>
    </div>
  );
}

export default function ReportView({
  report,
  onExportPdf,
  onBookmark,
}: {
  report: AnalysisReport;
  onExportPdf?: () => void;
  onBookmark?: () => void;
}) {
  const { ai_prediction: ai, domain_info: di, ssl_info: ssl, dns_info: dns, tech_stack: tech } = report;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* Header */}
      <Panel className="!p-6">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-4">
            {di.favicon && (
              <img src={di.favicon} alt="" className="h-10 w-10 rounded-md border border-line bg-panel object-contain p-1" />
            )}
            <div>
              <p className="font-display text-lg font-semibold text-ink">{di.title || di.domain}</p>
              <p className="text-xs text-ink-dim">{report.url}</p>
            </div>
          </div>
          <div className="flex gap-2">
            {onBookmark && (
              <button onClick={onBookmark} className="flex items-center gap-1.5 rounded-md border border-line px-3 py-2 text-xs font-medium text-ink-dim hover:text-signal hover:border-signal/40">
                <Bookmark size={13} /> Bookmark
              </button>
            )}
            {onExportPdf && (
              <button onClick={onExportPdf} className="flex items-center gap-1.5 rounded-md bg-signal px-3 py-2 text-xs font-semibold text-void hover:scale-[1.02] transition-transform">
                <Download size={13} /> Export PDF
              </button>
            )}
          </div>
        </div>
      </Panel>

      {/* Gauge + Reasons */}
      <div className="grid gap-6 md:grid-cols-[220px_1fr]">
        <Panel className="flex items-center justify-center !p-6">
          <RiskGauge score={ai.risk_score} verdict={ai.verdict} />
        </Panel>
        <Panel title="Why AI reached this verdict" icon={<ShieldAlert size={15} className="text-signal" />}>
          <ul className="space-y-2.5">
            {ai.reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-ink-dim">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-signal/70" />
                {r}
              </li>
            ))}
          </ul>
          <div className="mt-4 flex items-center gap-2 text-xs text-ink-faint">
            Confidence <span className="font-mono text-ink">{ai.confidence}%</span>
          </div>
        </Panel>
      </div>

      {/* Domain + SSL */}
      <div className="grid gap-6 md:grid-cols-2">
        <Panel title="Domain Intelligence" icon={<Globe size={15} className="text-signal" />}>
          <Row label="Domain" value={di.domain} />
          <Row label="IP Address" value={di.ip_address} />
          <Row label="IPv6" value={di.ipv6} />
          <Row label="Registrar" value={di.registrar} />
          <Row label="Created" value={di.creation_date?.slice(0, 10)} />
          <Row label="Expires" value={di.expiry_date?.slice(0, 10)} />
          <Row label="Domain Age" value={di.domain_age_days != null ? `${di.domain_age_days} days` : null} />
          <Row label="Hosting Provider" value={di.hosting_provider} />
          <Row label="ASN" value={di.asn} />
          <Row label="Country" value={di.country} />
          <Row label="City" value={di.city} />
          <Row label="CDN" value={di.cdn_provider} />
        </Panel>

        <Panel title="SSL / TLS Analysis" icon={<Lock size={15} className="text-signal" />}>
          <div className="mb-3 flex flex-wrap gap-2">
            <StatusPill status={ssl.https ? "strong" : "missing"} />
            {ssl.hsts && <StatusPill status="present" />}
          </div>
          <Row label="HTTPS Enabled" value={ssl.https ? "Yes" : "No"} />
          <Row label="Certificate Valid" value={ssl.valid ? "Yes" : "No"} />
          <Row label="Issuer" value={ssl.issuer} />
          <Row label="TLS Version" value={ssl.tls_version} />
          <Row label="Expiry" value={ssl.expiry_date?.slice(0, 10)} />
          <Row label="Days Remaining" value={ssl.days_remaining} />
          <Row label="HSTS" value={ssl.hsts ? "Enabled" : "Disabled"} />
          {ssl.error && <p className="mt-2 text-xs text-alert-critical">{ssl.error}</p>}
        </Panel>
      </div>

      {/* DNS + Headers */}
      <div className="grid gap-6 md:grid-cols-2">
        <Panel title="DNS Records" icon={<Server size={15} className="text-signal" />}>
          {(["a", "aaaa", "mx", "ns", "txt", "cname"] as const).map((k) => (
            <Row key={k} label={k.toUpperCase()} value={dns[k]?.length ? dns[k].join(", ") : null} />
          ))}
          <Row label="DNSSEC" value={dns.dnssec ? "Enabled" : "Not detected"} />
        </Panel>

        <Panel title="Security Headers" icon={<ShieldAlert size={15} className="text-signal" />}>
          <div className="space-y-2">
            {report.security_headers.map((h) => (
              <div key={h.name} className="flex items-center justify-between border-b border-line/50 py-1.5 last:border-0">
                <span className="text-xs text-ink-dim">{h.name}</span>
                <StatusPill status={h.status} />
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Tech + Reputation */}
      <div className="grid gap-6 md:grid-cols-2">
        <Panel title="Technology Stack" icon={<Fingerprint size={15} className="text-signal" />}>
          {Object.entries(tech).filter(([, v]) => (v as string[]).length).length === 0 ? (
            <p className="text-xs text-ink-faint">No technologies confidently detected.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {Object.entries(tech).flatMap(([, list]) =>
                (list as string[]).map((t) => (
                  <span key={t} className="rounded-md border border-line bg-void/60 px-2.5 py-1 text-xs text-ink-dim">
                    {t}
                  </span>
                ))
              )}
            </div>
          )}
        </Panel>

        <Panel title="Reputation & Blacklist Checks" icon={<ShieldAlert size={15} className="text-signal" />}>
          <div className="space-y-2.5">
            {report.reputation.map((r) => (
              <div key={r.source} className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-ink">{r.source}</p>
                  <p className="text-[11px] text-ink-faint">{r.detail}</p>
                </div>
                <StatusPill status={r.status} />
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Timeline */}
      <Panel title="Threat Analysis Timeline" icon={<Clock size={15} className="text-signal" />}>
        <div className="flex flex-wrap gap-3">
          {report.timeline.map((t, i) => (
            <div key={i} className="flex min-w-[140px] flex-1 items-center gap-3 rounded-lg border border-line bg-void/50 p-3">
              <div className={`h-2 w-2 rounded-full ${t.status === "done" ? "bg-signal" : t.status === "failed" ? "bg-alert-critical" : "bg-ink-faint"}`} />
              <div>
                <p className="text-xs font-medium text-ink">{t.step}</p>
                <p className="text-[11px] text-ink-faint">{t.duration_ms}ms</p>
              </div>
            </div>
          ))}
        </div>
      </Panel>

      {/* Screenshots */}
      {(report.screenshot_desktop || report.screenshot_mobile) && (
        <Panel title="Website Preview">
          <div className="grid gap-4 sm:grid-cols-2">
            {report.screenshot_desktop && (
              <img src={report.screenshot_desktop} alt="Desktop preview" className="w-full rounded-lg border border-line" />
            )}
            {report.screenshot_mobile && (
              <img src={report.screenshot_mobile} alt="Mobile preview" className="mx-auto max-w-[220px] rounded-lg border border-line" />
            )}
          </div>
        </Panel>
      )}
    </motion.div>
  );
}
