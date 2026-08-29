import { useEffect, useState } from "react";
import { getRequests } from "../api/requestsApi";
import { useAuth } from "../context/useAuth";
import StatusBadge from "../components/StatusBadge";

export default function DashboardPage({ refreshKey }) {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRequests(user.role).then(setRequests).finally(() => setLoading(false));
  }, [user.role, refreshKey]);

  const activeCount = requests.filter((r) => !["completed", "rejected"].includes(r.status)).length;

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-800 mb-1">Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6">
        {activeCount} active request{activeCount !== 1 ? "s" : ""} in {user.role}
      </p>

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