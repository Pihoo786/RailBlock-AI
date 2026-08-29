import { useEffect, useState } from "react";
import { getRequests } from "../api/requestsApi";
import { useAuth } from "../context/useAuth";
import StatusBadge from "../components/StatusBadge";

export default function HistoryPage({ refreshKey }) {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRequests(user.role).then(setRequests).finally(() => setLoading(false));
  }, [user.role, refreshKey]);

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-800 mb-6">Request History</h1>

      {loading && <p className="text-sm text-gray-400">Loading...</p>}
      {!loading && requests.length === 0 && <p className="text-sm text-gray-400">No requests yet.</p>}

      <div className="space-y-3">
        {requests.map((r) => (
          <div key={r.id} className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <p className="font-semibold text-gray-800 text-sm">{r.asset_id} &middot; {r.section}</p>
                <p className="text-xs text-gray-500">{r.category} &middot; {r.maintenance_type}</p>
              </div>
              <StatusBadge status={r.status} />
            </div>
            <p className="text-xs text-gray-400">
              Submitted {new Date(r.reported_date).toLocaleString()} by {r.submitted_by}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}