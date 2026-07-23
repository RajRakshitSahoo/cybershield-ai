import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { LayoutDashboard } from "lucide-react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { getDashboardSummary } from "../lib/api";
import Panel from "../components/Panel";

const VERDICT_COLORS: Record<string, string> = { Safe: "#39ffb0", Suspicious: "#ffd23f", Phishing: "#ff4d6a" };

export default function Dashboard() {
  const [data, setData] = useState<any | null>(null);

  useEffect(() => {
    getDashboardSummary().then(setData);
  }, []);

  if (!data) return <div className="flex min-h-[60vh] items-center justify-center text-xs text-ink-faint">Loading dashboard…</div>;

  const verdictData = Object.entries(data.verdict_distribution).map(([name, value]) => ({ name, value }));
  const dayData = Object.entries(data.scans_by_day).map(([date, count]) => ({ date: date.slice(5), count }));
  const tldData = Object.entries(data.top_tlds).map(([tld, count]) => ({ tld: `.${tld}`, count }));

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex items-center gap-2">
        <LayoutDashboard size={18} className="text-signal" />
        <h1 className="font-display text-2xl font-semibold text-ink">Your Dashboard</h1>
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-3">
        <StatCard label="Total Scans" value={data.total_scans} />
        <StatCard label="Average Risk Score" value={`${data.average_risk_score}/100`} />
        <StatCard label="Safe Rate" value={`${data.total_scans ? Math.round(((data.verdict_distribution.Safe || 0) / data.total_scans) * 100) : 0}%`} />
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <Panel title="Verdict Distribution">
          {verdictData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={verdictData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                  {verdictData.map((d) => (
                    <Cell key={d.name} fill={VERDICT_COLORS[d.name as string] || "#8a95ab"} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f1523", border: "1px solid #1c2436", fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState />
          )}
        </Panel>

        <Panel title="Scans Over Time">
          {dayData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={dayData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1c2436" />
                <XAxis dataKey="date" stroke="#4d5871" fontSize={11} />
                <YAxis stroke="#4d5871" fontSize={11} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0f1523", border: "1px solid #1c2436", fontSize: 12 }} />
                <Bar dataKey="count" fill="#39ffb0" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState />
          )}
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <Panel title="Most Common TLDs">
          {tldData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={tldData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1c2436" />
                <XAxis type="number" stroke="#4d5871" fontSize={11} allowDecimals={false} />
                <YAxis type="category" dataKey="tld" stroke="#4d5871" fontSize={11} width={50} />
                <Tooltip contentStyle={{ background: "#0f1523", border: "1px solid #1c2436", fontSize: 12 }} />
                <Bar dataKey="count" fill="#39ffb0" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState />
          )}
        </Panel>

        <Panel title="Top Countries">
          <div className="space-y-3">
            {Object.entries(data.top_countries).length === 0 && <EmptyState />}
            {Object.entries(data.top_countries).map(([country, count]) => (
              <div key={country} className="flex items-center justify-between text-sm">
                <span className="text-ink-dim">{country}</span>
                <span className="font-mono text-ink">{count as number}</span>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </motion.div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="panel rounded-xl p-5">
      <p className="text-xs text-ink-faint">{label}</p>
      <p className="mt-2 font-display text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}

function EmptyState() {
  return <p className="py-10 text-center text-xs text-ink-faint">Not enough data yet — run a few scans.</p>;
}
