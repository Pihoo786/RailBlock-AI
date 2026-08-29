import { useState } from "react";
import { TrainFront } from "lucide-react";
import { ROLES } from "../data/roles";
import { useAuth } from "../context/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [role, setRole] = useState(ROLES[0].id);

  function handleSubmit() {
    if (!username.trim()) return;
    login(username.trim(), role);
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-8 w-full max-w-sm">
        <div className="flex items-center gap-2 mb-6">
          <TrainFront size={22} className="text-[#1E3A5F]" />
          <span className="text-lg font-extrabold text-[#1E3A5F] tracking-tight">RailBlock Dept Portal</span>
        </div>

        <label className="text-sm text-gray-500">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. eng_officer1"
          className="w-full mt-1 mb-4 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
        />

        <label className="text-sm text-gray-500">Department</label>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full mt-1 mb-6 border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#2563EB]"
        >
          {ROLES.map((r) => (
            <option key={r.id} value={r.id}>{r.label}</option>
          ))}
        </select>

        <button
          onClick={handleSubmit}
          className="w-full bg-[#1E3A5F] text-white font-semibold py-2.5 rounded-lg hover:opacity-90"
        >
          Log In
        </button>
      </div>
    </div>
  );
}