import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { getRequests } from "../api/requestsApi";
import { useAuth } from "../context/useAuth";
import { STATUS_LABELS } from "../data/statuses";
import { ROLES } from "../data/roles";

const SEVERITY_COLORS = { LOW: "#64748B", MEDIUM: "#2563EB", HIGH: "#B91C1C", CRITICAL: "#7C2D12" };

export default function AnalyticsPage({ refreshKey }) {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    const departmentValue = ROLES.find((r) => r.id === user.role)?.apiValue;
    getRequests(departmentValue).then(setRequests);
  }, [user.role, refreshKey]);

  const statusData = Object.keys(STATUS_LABELS).map((key) => ({
    name: STATUS_LABELS[key],
    count: requests.filter((r) => r.status === key).length,
  }));

  const severityData = ["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((level) => ({
    name: level,
    value: requests.filter((r) => r.severity === level).length,
  }))

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-800 mb-1">Analytics</h1>
      <p className="text-sm text-gray-500 mb-6 capitalize">{user.role} request breakdown</p>

      {requests.length === 0 ? (
        <p className="text-sm text-gray-400">Submit a few requests to see analytics here.</p>
      ) : (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <p className="text-sm font-semibold text-gray-700 mb-4">Requests by Status</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={statusData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#1E3A5F" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <p className="text-sm font-semibold text-gray-700 mb-4">Requests by Severity</p>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={severityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                  {severityData.map((entry) => (
                    <Cell key={entry.name} fill={SEVERITY_COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}