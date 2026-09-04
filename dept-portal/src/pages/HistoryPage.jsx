import { useEffect, useState } from "react";
import { getRequests } from "../api/requestsApi";
import { useAuth } from "../context/useAuth";
import StatusBadge from "../components/StatusBadge";
import { ROLES } from "../data/roles";

export default function HistoryPage({ refreshKey }) {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const departmentValue = ROLES.find((r) => r.id === user.role)?.apiValue;
    getRequests(departmentValue).then(setRequests).finally(() => setLoading(false));
  }, [user.role, refreshKey]);

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-800 mb-6">Request History</h1>

      {loading && <p className="text-sm text-gray-400">Loading...</p>}
      {!loading && requests.length === 0 && <p className="text-sm text-gray-400">No requests yet.</p>}

      <div className="space-y-3">
        {requests.map((request) => (
          <div key={request.id} className="bg-white border border-gray-200 rounded-xl p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <p className="font-semibold text-gray-800 text-sm">{request.asset_id} &middot; {request.section}</p>
                <p className="text-xs text-gray-500">{request.category} &middot; {request.maintenance_type}</p>
                {request.nlp_category && request.nlp_category !== request.category && (
                  <p className="text-xs text-amber-600 mt-0.5">
                    ⚠ Category mismatch — NLP detected: {request.nlp_category}
                  </p>
                )}
              </div>
              <div className="text-right">
                <StatusBadge status={request.status} />
                {request.final_severity && (
                  <p className="text-xs text-gray-400 mt-1">
                    Severity: {request.severity} → <span className="font-semibold text-gray-600">{request.final_severity}</span>
                  </p>
                )}
              </div>
            </div>
            <p className="text-xs text-gray-400">
              Submitted {new Date(request.reported_date).toLocaleString()} by {request.submitted_by}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}