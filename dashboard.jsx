import React, { useState } from 'react';
import { mockSummaryStats, mockRecommendations, mockHighRiskAssets } from '../data/mockData';

export default function RailwayDashboard() {
  const [recommendations, setRecommendations] = useState(mockRecommendations);

  const handleAction = (id, newStatus) => {
    setRecommendations(prev =>
      prev.map(rec => rec.id === id ? { ...rec, status: newStatus } : rec)
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
      {/* Top Header */}
      <header className="mb-8 border-b border-slate-700 pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-wide text-amber-400">
            RAILWAY CONTROL CENTRE
          </h1>
          <p className="text-sm text-slate-400">Automatic Maintenance Block Planning System</p>
        </div>
        <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-xs font-semibold border border-emerald-500/30">
          SYSTEM ONLINE
        </span>
      </header>

      {/* Summary Metrics Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <MetricCard label="Active Trains" value={mockSummaryStats.activeTrains} color="text-blue-400" />
        <MetricCard label="Recommended Blocks text-amber-400" value={mockSummaryStats.recommendedBlocks} color="text-amber-400" />
        <MetricCard label="Conflicts Detected" value={mockSummaryStats.conflictsDetected} color="text-rose-400" />
        <MetricCard label="High-Risk Assets" value={mockSummaryStats.highRiskAssets} color="text-purple-400" />
      </div>

      {/* Main Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Section (2 cols): AI Recommendations Card */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-semibold text-slate-300">AI Block Recommendations</h2>
          
          {recommendations.map((rec) => (
            <div key={rec.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-slate-700 text-slate-300">
                    {rec.id}
                  </span>
                  <h3 className="text-xl font-bold mt-1 text-white">{rec.section}</h3>
                </div>
                <StatusBadge status={rec.status} />
              </div>

              {/* Block Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-slate-900/60 p-4 rounded-lg my-4 text-sm">
                <div>
                  <p className="text-slate-400 text-xs">TIME WINDOW</p>
                  <p className="font-semibold text-amber-300">{rec.startTime} – {rec.endTime}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">DEPARTMENTS</p>
                  <p className="font-semibold">{rec.departments.join(' + ')}</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">AFFECTED TRAINS</p>
                  <p className="font-semibold text-rose-400">{rec.affectedTrainsCount} Train(s)</p>
                </div>
                <div>
                  <p className="text-slate-400 text-xs">EXPECTED DELAY</p>
                  <p className="font-semibold">{rec.expectedDelayMinutes} mins</p>
                </div>
              </div>

              {/* Action Buttons */}
              {rec.status === 'RECOMMENDED' && (
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={() => handleAction(rec.id, 'APPROVED')}
                    className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded-lg transition"
                  >
                    APPROVE
                  </button>
                  <button
                    onClick={() => handleAction(rec.id, 'REJECTED')}
                    className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 px-4 rounded-lg transition"
                  >
                    REJECT
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Right Section (1 col): High-Risk Assets List */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-slate-300">High-Risk Assets</h2>
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 divide-y divide-slate-700">
            {mockHighRiskAssets.map((asset) => (
              <div key={asset.id} className="py-3 flex justify-between items-center text-sm">
                <div>
                  <p className="font-semibold text-slate-200">{asset.id} <span className="text-xs text-slate-400">({asset.type})</span></p>
                  <p className="text-xs text-slate-400">{asset.location} • {asset.department}</p>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                    Risk: {asset.riskScore}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

// Helper Components
function MetricCard({ label, value, color }) {
  return (
    <div className="bg-slate-800 border border-slate-700 p-4 rounded-xl">
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    RECOMMENDED: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    APPROVED: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    REJECTED: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
  };
  return (
    <span className={`text-xs font-bold px-3 py-1 rounded-full border ${styles[status]}`}>
      {status}
    </span>
  );
}
