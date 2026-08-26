import React, { useEffect, useState } from 'react';
import { getDashboardData, updateBlockStatus } from "../api/dashboardApi";

export default function RailwayDashboard() {
  const [summaryStats, setSummaryStats] = useState({
    activeTrains: 0,
    recommendedBlocks: 0,
    conflictsDetected: 0,
    highRiskAssets: 0,
  });

  const [recommendations, setRecommendations] = useState([]);
  const [highRiskAssets, setHighRiskAssets] = useState([]);
  const [selectedRec, setSelectedRec] = useState(null);
  const [activeTab, setActiveTab] = useState('DASHBOARD');
  const [loading, setLoading] = useState(true);
  const handleAction = async (id, newStatus) => {
    try {
      const action =
        newStatus === "APPROVED" ? "approve" : "reject";

      await updateBlockStatus(id, action);

      setRecommendations((prev) =>
        prev.map((rec) =>
          rec.id === id ? { ...rec, status: newStatus } : rec
        )
      );

      if (selectedRec?.id === id) {
        setSelectedRec((prev) => ({
          ...prev,
          status: newStatus,
        }));
      }
    } catch (error) {
      console.error(`Failed to update block:`, error);
      alert("Could not update this block");
    }
  };
  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await getDashboardData();

        setSummaryStats(data.summaryStats);
        setRecommendations(data.recommendations);
        setHighRiskAssets(data.highRiskAssets);

        if (data.recommendations.length > 0) {
          setSelectedRec(data.recommendations[0]);
        }
      } catch (error) {
        console.error("Dashboard API failed:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <div className="min-h-screen bg-[#F7F9FB] text-slate-800 font-sans flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-[#F7F9FB] p-6 flex flex-col gap-6 shrink-0 border-r border-slate-200/60">
        <div className="py-2">
          <h2 className="text-xl font-bold tracking-tight text-[#2C5F8A]">RailBlock AI</h2>
        </div>

        <nav className="flex flex-col gap-1 text-xs font-semibold tracking-wide uppercase">
          <button
            onClick={() => setActiveTab('DASHBOARD')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition ${
              activeTab === 'DASHBOARD'
                ? 'bg-[#EAF1F7] text-[#2C5F8A]'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Dashboard
          </button>

          <button
            onClick={() => setActiveTab('RECOMMENDATIONS')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition ${
              activeTab === 'RECOMMENDATIONS'
                ? 'bg-[#EAF1F7] text-[#2C5F8A]'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Recommendations
          </button>

          <button
            onClick={() => setActiveTab('ASSETS')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition ${
              activeTab === 'ASSETS'
                ? 'bg-[#EAF1F7] text-[#2C5F8A]'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Assets
          </button>

          <button
            onClick={() => setActiveTab('CONFIGURATION')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition ${
              activeTab === 'CONFIGURATION'
                ? 'bg-[#EAF1F7] text-[#2C5F8A]'
                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            </svg>
            Configuration
          </button>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-10 max-w-7xl">
        {/* Header Bar */}
        <header className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-[#2C5F8A] tracking-tight">
            Railway Control Centre
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            AI-Powered Automatic Maintenance Block Planning System • Corridor: NDLS-CNB
          </p>

          <div className="mt-4 bg-[#EAF1F7] px-4 py-2.5 rounded-xl inline-flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-600">Active System Mode</span>
            <span className="text-xs font-bold text-[#2C5F8A] uppercase tracking-wider">
              Optimization Engine Online
            </span>
          </div>
        </header>

        {/* Metric Summary Bar */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <MetricCard label="Active Trains on Section" value={summaryStats.activeTrains} />
          <MetricCard label="Proposed Maintenance Blocks" value={summaryStats.recommendedBlocks} />
          <MetricCard label="Train Conflicts Detected" value={summaryStats.conflictsDetected} />
          <MetricCard label="High-Risk Assets" value={summaryStats.highRiskAssets} />
        </section>

        {/* Primary Screen Area: Focal Cards Stack */}
        <div className="space-y-8">
          
          {/* Main Focal Card: Primary Block Recommendation */}
          <section>
            <h2 className="text-base font-bold text-slate-900 mb-4">
              AI Block Recommendations ({recommendations.length})
            </h2>

            <div className="space-y-4">
              {recommendations.map((rec) => (
                <div
                  key={rec.id}
                  onClick={() => setSelectedRec(rec)}
                  className={`bg-white rounded-2xl p-6 md:p-8 shadow-sm border transition cursor-pointer ${
                    selectedRec?.id === rec.id
                      ? 'border-[#2C5F8A] ring-1 ring-[#2C5F8A]/20'
                      : 'border-slate-200/80 hover:border-slate-300'
                  }`}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-semibold text-slate-500 font-mono">
                          {rec.id}
                        </span>
                        <span className="text-[11px] font-bold tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md uppercase">
                          {rec.impactLevel} Impact
                        </span>
                        <StatusWord status={rec.status} />
                      </div>

                      <h3 className="text-xl font-bold text-[#2C5F8A]">
                        {rec.section}
                      </h3>
                    </div>

                    {/* Operational Quick Metrics */}
                    <div className="flex items-center gap-6 text-sm text-slate-600">
                      <div>
                        <span className="text-xs text-slate-400 block font-medium">Affected Trains:</span>
                        <span className="font-bold text-slate-800">{rec.affectedTrainsCount}</span>
                      </div>
                      <div className="h-8 w-px bg-slate-200"></div>
                      <div>
                        <span className="text-xs text-slate-400 block font-medium">Est. Max Delay:</span>
                        <span className="font-bold text-slate-800">{rec.expectedDelayMinutes} mins</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-xs text-slate-600">
                        <strong className="text-slate-800 font-semibold">Job Scope:</strong> {rec.reason}
                      </p>
                      <p className="text-xs text-slate-600">
                        <strong className="text-slate-800 font-semibold">Window:</strong> {rec.startTime} – {rec.endTime}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      {rec.departments.map((dept) => (
                        <span key={dept} className="text-xs text-slate-600 bg-slate-100 px-3 py-1 rounded-md font-medium">
                          #{dept}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  {rec.status === 'RECOMMENDED' && (
                    <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end gap-3" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleAction(rec.id, 'APPROVED')}
                        className="bg-[#2C5F8A] hover:bg-[#234b6e] text-white text-xs font-bold px-6 py-2.5 rounded-xl transition shadow-sm"
                      >
                        Approve Block
                      </button>
                      <button
                        onClick={() => handleAction(rec.id, 'REJECTED')}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-6 py-2.5 rounded-xl transition"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Critical Asset Risk Queue Focal Card Table */}
          <section className="bg-white rounded-2xl p-6 md:p-8 shadow-sm border border-slate-200/80">
            <h2 className="text-base font-bold text-slate-900 mb-6">
              Critical Asset Risk Queue
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead>
                  <tr className="border-b border-slate-100 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <th className="pb-3 font-medium">Asset ID</th>
                    <th className="pb-3 font-medium">Risk Priority</th>
                    <th className="pb-3 font-medium">Risk Score</th>
                    <th className="pb-3 font-medium">Department</th>
                    <th className="pb-3 font-medium">Location</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {highRiskAssets.map((asset) => (
                    <tr key={asset.id} className="hover:bg-slate-50/50 transition">
                      <td className="py-4 font-mono font-bold text-slate-900">{asset.id}</td>
                      <td className="py-4 font-bold text-xs uppercase">
                        <span className={asset.priority === 'CRITICAL' ? 'text-rose-600' : asset.priority === 'HIGH' ? 'text-amber-600' : 'text-slate-500'}>
                          {asset.priority}
                        </span>
                      </td>
                      <td className="py-4 font-bold text-amber-700 font-mono">{asset.riskScore}</td>
                      <td className="py-4 text-slate-700">{asset.department}</td>
                      <td className="py-4 text-slate-500">{asset.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}

/* Rounded Clean Metric Card Component */
function MetricCard({ label, value }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
      <p className="text-xs font-bold text-slate-500 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-black text-[#2C5F8A] mt-3 tracking-tight">{value}</p>
    </div>
  );
}

/* Status Words — Strictly Text Formatting without heavy backgrounds */
function StatusWord({ status }) {
  if (status === 'APPROVED') {
    return (
      <span className="text-xs font-bold text-emerald-600 uppercase flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
        Approved
      </span>
    );
  }
  if (status === 'REJECTED') {
    return (
      <span className="text-xs font-bold text-slate-400 uppercase flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-slate-400"></span>
        Rejected
      </span>
    );
  }
  return (
    <span className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1.5">
      <span className="w-2 h-2 rounded-full bg-slate-400"></span>
      Recommended
    </span>
  );
}