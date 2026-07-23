import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldCheck, Loader2 } from "lucide-react";
import { useAuth } from "../lib/auth";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register(name, email, password);
      navigate("/dashboard");
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Could not create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[80vh] max-w-md flex-col justify-center px-6 py-16">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="panel rounded-2xl p-8">
        <div className="mb-6 flex items-center gap-2">
          <ShieldCheck size={20} className="text-signal" />
          <h1 className="font-display text-lg font-semibold text-ink">Create your account</h1>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-dim">Name</label>
            <input
              required value={name} onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-line bg-void px-3.5 py-2.5 text-sm text-ink focus:border-signal/50 focus:outline-none focus:ring-1 focus:ring-signal/30"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-dim">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-line bg-void px-3.5 py-2.5 text-sm text-ink focus:border-signal/50 focus:outline-none focus:ring-1 focus:ring-signal/30"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-dim">Password</label>
            <input
              type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-line bg-void px-3.5 py-2.5 text-sm text-ink focus:border-signal/50 focus:outline-none focus:ring-1 focus:ring-signal/30"
            />
          </div>
          {error && <p className="text-xs text-alert-critical">{error}</p>}
          <button
            type="submit" disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-signal py-2.5 text-sm font-semibold text-void shadow-glow transition-transform hover:scale-[1.01] disabled:opacity-60"
          >
            {loading && <Loader2 size={15} className="animate-spin" />}
            Create account
          </button>
        </form>
        <p className="mt-6 text-center text-xs text-ink-dim">
          Already registered? <Link to="/login" className="font-medium text-signal">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
