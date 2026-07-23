interface Props {
  status: string;
  size?: "sm" | "md";
}

const STYLES: Record<string, string> = {
  safe: "text-signal bg-signal/10 border-signal/30",
  clean: "text-signal bg-signal/10 border-signal/30",
  strong: "text-signal bg-signal/10 border-signal/30",
  present: "text-signal bg-signal/10 border-signal/30",
  done: "text-signal bg-signal/10 border-signal/30",

  suspicious: "text-alert-medium bg-alert-medium/10 border-alert-medium/30",
  weak: "text-alert-medium bg-alert-medium/10 border-alert-medium/30",

  phishing: "text-alert-critical bg-alert-critical/10 border-alert-critical/30",
  blacklisted: "text-alert-critical bg-alert-critical/10 border-alert-critical/30",
  missing: "text-alert-critical bg-alert-critical/10 border-alert-critical/30",
  failed: "text-alert-critical bg-alert-critical/10 border-alert-critical/30",

  unavailable: "text-ink-faint bg-ink-faint/5 border-line",
  skipped: "text-ink-faint bg-ink-faint/5 border-line",
};

export default function StatusPill({ status, size = "sm" }: Props) {
  const key = status?.toLowerCase() ?? "";
  const cls = STYLES[key] ?? "text-ink-dim bg-panel border-line";
  return (
    <span
      className={`inline-flex items-center rounded-full border font-semibold uppercase tracking-wide ${cls} ${
        size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-3 py-1 text-xs"
      }`}
    >
      {status}
    </span>
  );
}
