import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { Bot } from "lucide-react";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [form, setForm] = useState({ email: "", username: "", password: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();
    const ok = await register(form.email, form.username, form.password);
    if (ok) navigate("/");
  };

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center">
            <Bot size={22} className="text-white" />
          </div>
          <div>
            <div className="text-xl font-bold text-white">AgentOS</div>
            <div className="text-xs text-gray-500">Multi-Agent System</div>
          </div>
        </div>

        <div className="card space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Create account</h2>
            <p className="text-sm text-gray-500">Get started for free</p>
          </div>

          {error && (
            <div className="bg-red-950 border border-red-800 text-red-300 text-sm rounded-lg p-3">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Email</label>
              <input type="email" value={form.email} onChange={update("email")}
                className="input" placeholder="you@example.com" required />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Username</label>
              <input type="text" value={form.username} onChange={update("username")}
                className="input" placeholder="cooluser" required minLength={3} />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1.5">Password</label>
              <input type="password" value={form.password} onChange={update("password")}
                className="input" placeholder="Min 8 characters" required minLength={8} />
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary w-full py-2.5">
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account...
                </span>
              ) : "Create account"}
            </button>
          </form>

          <p className="text-sm text-gray-500 text-center">
            Already have an account?{" "}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
