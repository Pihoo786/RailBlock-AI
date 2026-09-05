import { useEffect, useState } from "react";
import { ClipboardList, Activity, CheckCircle2, XCircle } from "lucide-react";
import { getRequests } from "../api/requestsApi";
import { useAuth } from "../context/useAuth";
import StatusBadge from "../components/StatusBadge";
import { ROLES } from "../data/roles";

export default function DashboardPage({ refreshKey }) {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const departmentValue = ROLES.find((r) => r.id === user.role)?.apiValue;
    getRequests(departmentValue).then(setRequests).finally(() => setLoading(false));
  }, [user.role, refreshKey]);

  const total = requests.length;
  const active = requests.filter((r) => !["completed", "rejected"].includes(r.status)).length;
  const completed = requests.filter((r) => r.status === "completed").length;
  const rejected = requests.filter((r) => r.status === "rejected").length;

  const stats = [
    { label: "Total Requests", value: total, icon: ClipboardList, color: "text-[#1E3A5F]" },
    { label: "Active", value: active, icon: Activity, color: "text-amber-600" },
    { label: "Completed", value: completed, icon: CheckCircle2, color: "text-emerald-600" },
    { label: "Rejected", value: rejected, icon: XCircle, color: "text-red-600" },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-800 mb-1">Welcome back, {user.username}</h1>
      <p className="text-sm text-gray-500 mb-6 capitalize">{user.role} Department Overview</p>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="bg-white border border-gray-200 rounded-2xl p-4">
              <Icon size={18} className={s.color} />
              <p className="text-2xl font-extrabold text-gray-800 mt-2">{s.value}</p>
              <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
            </div>
          );
        })}
      </div>

      <h2 className="text-sm font-semibold text-gray-600 mb-3">Recent Requests</h2>
      {loading && <p className="text-sm text-gray-400">Loading...</p>}
      {!loading && requests.length === 0 && (
        <p className="text-sm text-gray-400">No requests submitted yet.</p>
      )}

      <div className="space-y-3">
        {requests.slice(0, 5).map((r) => (
          <div key={r.id} className="bg-white border border-gray-200 rounded-xl p-4 flex justify-between items-center">
            <div>
              <p className="font-semibold text-gray-800 text-sm">{r.asset_id} &middot; {r.section}</p>
              <p className="text-xs text-gray-500">{r.category}</p>
            </div>
            <StatusBadge status={r.status} />
          </div>
        ))}
      </div>
    </div>
  );
}