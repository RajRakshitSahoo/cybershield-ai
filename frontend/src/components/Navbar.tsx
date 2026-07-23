import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, LayoutDashboard, History, GitCompare, LogOut, LockKeyhole } from "lucide-react";
import { useAuth } from "../lib/auth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-void/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="relative flex h-8 w-8 items-center justify-center rounded-md border border-signal/30 bg-signal/10">
            <ShieldCheck size={18} className="text-signal" />
            <span className="absolute inset-0 rounded-md border border-signal/0 group-hover:border-signal/40 transition-colors" />
          </div>
          <span className="font-display text-[15px] font-semibold tracking-tight text-ink">
            CyberShield <span className="text-signal">AI</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavLink to="/" label="Scanner" />
          {user && <NavLink to="/dashboard" label="Dashboard" icon={<LayoutDashboard size={14} />} />}
          {user && <NavLink to="/history" label="History" icon={<History size={14} />} />}
          <NavLink to="/compare" label="Compare" icon={<GitCompare size={14} />} />
          {user?.role === "admin" && <NavLink to="/admin" label="Admin" icon={<LockKeyhole size={14} />} />}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden text-xs text-ink-dim sm:block">{user.email}</span>
              <button
                onClick={() => { logout(); navigate("/"); }}
                className="flex items-center gap-1.5 rounded-md border border-line px-3 py-1.5 text-xs font-medium text-ink-dim transition-colors hover:border-alert-critical/40 hover:text-alert-critical"
              >
                <LogOut size={13} /> Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="rounded-md px-3 py-1.5 text-xs font-medium text-ink-dim hover:text-ink">
                Sign in
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-signal px-3.5 py-1.5 text-xs font-semibold text-void shadow-glow transition-transform hover:scale-[1.03]"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function NavLink({ to, label, icon }: { to: string; label: string; icon?: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium text-ink-dim transition-colors hover:bg-panel hover:text-ink"
    >
      {icon}
      {label}
    </Link>
  );
}
