import { ShieldCheck } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-line/70 bg-void">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-2">
            <ShieldCheck size={16} className="text-signal" />
            <span className="font-display text-sm font-semibold text-ink">CyberShield AI</span>
          </div>
          <p className="max-w-md text-xs leading-relaxed text-ink-faint">
            Domain intelligence and AI phishing detection for research and awareness purposes.
            Always verify critical findings through multiple independent sources.
          </p>
          <div className="flex gap-6 text-xs text-ink-dim">
            <span>API</span>
            <span>Docs</span>
            <span>GitHub</span>
          </div>
        </div>
        <div className="mt-8 border-t border-line/60 pt-6 text-[11px] text-ink-faint">
          Built as a final-year cybersecurity project &mdash; CyberShield AI, {new Date().getFullYear()}.
        </div>
      </div>
    </footer>
  );
}
