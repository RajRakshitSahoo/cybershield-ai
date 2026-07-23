import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { LockKeyhole, Users, ScanLine, ShieldAlert } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from "recharts";
import { getAdminStats, getAdminUsers } from "../lib/api";
import Panel from "../components/Panel";
import StatusPill from "../components/StatusPill";

export default function Admin() {
  const [stats, setStats] = useState<any | null>(null);
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    getAdminStats().then(setStats);
    getAdminUsers().then(setUsers);
  }, []);

  if (!stats) return <div className="flex min-h-[60vh] items-center justify-center text-xs text-ink-faint">Loading admin console…</div>;

  const dailyData = Object.entries(stats.daily_scans).map(([date, count]) => ({ date: (date as string).slice(5), count }));

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex items-center gap-2">
        <LockKeyhole size={18} className="text-signal" />
        <h1 className="font-display text-2xl font-semibold text-ink">Admin Console</h1>
      </div>

      <div className="mt-8 grid gap-5 sm:grid-cols-3">
        <MetricCard icon={<Users size={16} />} label="Total Users" value={stats.total_users} />
        <MetricCard icon={<ScanLine size={16} />} label="Total Scans" value={stats.total_scans} />
        <MetricCard icon={<ShieldAlert size={16} />} label="Phishing Detected" value={stats.verdict_distribution.Phishing || 0} />
      </div>

      <div className="mt-6">
        <Panel title="Daily Scan Volume">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c2436" />
              <XAxis dataKey="date" stroke="#4d5871" fontSize={11} />
              <YAxis stroke="#4d5871" fontSize={11} allowDecimals={false} />
              <Tooltip contentStyle={{ background: "#0f1523", border: "1px solid #1c2436", fontSize: 12 }} />
              <Bar dataKey="count" fill="#39ffb0" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <Panel title="Top Phishing Domains">
          <div className="space-y-2.5">
            {Object.entries(stats.top_phishing_domains).length === 0 && (
              <p className="text-xs text-ink-faint">No phishing domains detected yet.</p>
            )}
            {Object.entries(stats.top_phishing_domains).map(([domain, count]) => (
              <div key={domain} className="flex items-center justify-between text-sm">
                <span className="truncate text-ink-dim">{domain}</span>
                <span className="font-mono text-alert-critical">{count as number}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Recent Detections">
          <div className="space-y-2.5">
            {stats.recent_detections.map((d: any, i: number) => (
              <div key={i} className="flex items-center justify-between gap-2 border-b border-line/50 pb-2 last:border-0">
                <span className="truncate text-xs text-ink-dim">{d.url}</span>
                <StatusPill status={d.verdict} />
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="mt-6">
        <Panel title="User Management">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-line/60 text-[11px] uppercase tracking-wide text-ink-faint">
                  <th className="pb-2 pr-4">Name</th>
                  <th className="pb-2 pr-4">Email</th>
                  <th className="pb-2 pr-4">Role</th>
                  <th className="pb-2">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-line/40 last:border-0">
                    <td className="py-2 pr-4 text-ink">{u.name}</td>
                    <td className="py-2 pr-4 text-ink-dim">{u.email}</td>
                    <td className="py-2 pr-4"><StatusPill status={u.role === "admin" ? "strong" : "present"} /></td>
                    <td className="py-2 text-ink-faint">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </motion.div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="panel rounded-xl p-5">
      <div className="flex items-center gap-2 text-signal">{icon}<span className="text-xs text-ink-faint">{label}</span></div>
      <p className="mt-2 font-display text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}
