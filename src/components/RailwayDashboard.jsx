import React, { useState } from 'react';
import { 
  mockSummaryStats, 
  mockRecommendations, 
  mockHighRiskAssets, 
  mockYardAvailability, 
  mockEmergencyAlert 
} from '../data/mockdata.js';

export default function RailwayDashboard() {
  const [recommendations, setRecommendations] = useState(mockRecommendations);
  const [selectedRec, setSelectedRec] = useState(mockRecommendations[0]);
  const [activeTab, setActiveTab] = useState('DASHBOARD');
  
  // Emergency Overlay State
  const [showAlert, setShowAlert] = useState(true);

  const handleAction = (id, newStatus) => {
    setRecommendations((prev) =>
      prev.map((rec) => (rec.id === id ? { ...rec, status: newStatus } : rec))
    );
    if (selectedRec?.id === id) {
      setSelectedRec((prev) => ({ ...prev, status: newStatus }));
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F9FB] text-slate-800 font-sans flex flex-col md:flex-row relative">
      
      {/* Emergency Alert Panel Overlay */}
      {showAlert && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 md:p-8 max-w-lg w-full border-2 border-rose-500 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <span className="p-2 bg-rose-100 text-rose-600 rounded-xl animate-pulse">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              <div>
                <h3 className="text-base font-bold text-rose-600 uppercase tracking-wide">Emergency Obstacle Alert</h3>
                <p className="text-xs text-slate-500">{mockEmergencyAlert.timestamp}</p>
              </div>
            </div>

            <p className="text-slate-800 font-semibold text-sm">{mockEmergencyAlert.title}</p>
            <p className="text-xs text-slate-600"><strong>Location:</strong> {mockEmergencyAlert.location}</p>
            
            <div className="bg-rose-50 p-3 rounded-xl border border-rose-100 text-xs text-rose-800">
              <strong>System Action:</strong> {mockEmergencyAlert.recommendedAction}
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button 
                onClick={() => setShowAlert(false)} 
                className="bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs px-5 py-2.5 rounded-xl cursor-pointer"
              >
                Acknowledge & Dispatch ATP Signal
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 bg-[#F7F9FB] p-6 flex flex-col gap-6 shrink-0 border-r border-slate-200/60">
        <div className="py-2 flex justify-between items-center">
          <h2 className="text-xl font-bold tracking-tight text-[#2C5F8A]">RailBlock AI</h2>
        </div>

        <nav className="flex flex-col gap-1 text-xs font-semibold tracking-wide uppercase">
          <button
            onClick={() => setActiveTab('DASHBOARD')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer ${
              activeTab === 'DASHBOARD' ? 'bg-[#EAF1F7] text-[#2C5F8A]' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            Dashboard
          </button>

          <button
            onClick={() => setActiveTab('RECOMMENDATIONS')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer ${
              activeTab === 'RECOMMENDATIONS' ? 'bg-[#EAF1F7] text-[#2C5F8A]' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            Recommendations
          </button>

          <button
            onClick={() => setActiveTab('YARD')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer ${
              activeTab === 'YARD' ? 'bg-[#EAF1F7] text-[#2C5F8A]' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            Rolling Stock & Yard
          </button>

          <button
            onClick={() => setActiveTab('ASSETS')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition cursor-pointer ${
              activeTab === 'ASSETS' ? 'bg-[#EAF1F7] text-[#2C5F8A]' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-100'
            }`}
          >
            Assets
          </button>
        </nav>

        {/* Trigger emergency alert manually for testing */}
        <div className="mt-auto pt-4 border-t border-slate-200">
          <button 
            onClick={() => setShowAlert(true)}
            className="w-full text-left text-xs text-rose-600 font-bold hover:underline"
          >
             Simulate LC Obstacle Alert
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-10 max-w-7xl">
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

        {/* TAB 1: MAIN DASHBOARD & RECOMMENDATIONS */}
        {(activeTab === 'DASHBOARD' || activeTab === 'RECOMMENDATIONS') && (
          <div className="space-y-8">
            <section className="grid grid-cols-2 lg:grid-cols-4 gap-5">
              <MetricCard label="Active Trains on Section" value={mockSummaryStats.activeTrains} />
              <MetricCard label="Proposed Maintenance Blocks" value={mockSummaryStats.recommendedBlocks} />
              <MetricCard label="Train Conflicts Detected" value={mockSummaryStats.conflictsDetected} />
              <MetricCard label="High-Risk Assets" value={mockSummaryStats.highRiskAssets} />
            </section>

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
                      selectedRec?.id === rec.id ? 'border-[#2C5F8A] ring-1 ring-[#2C5F8A]/20' : 'border-slate-200/80 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-sm font-semibold text-slate-500 font-mono">{rec.id}</span>
                          <span className="text-[11px] font-bold tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md uppercase">
                            {rec.impactLevel} Impact
                          </span>
                          <StatusWord status={rec.status} />
                        </div>
                        <h3 className="text-xl font-bold text-[#2C5F8A]">{rec.section}</h3>
                      </div>

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

                    {rec.status === 'RECOMMENDED' && (
                      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-end gap-3" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => handleAction(rec.id, 'APPROVED')}
                          className="bg-[#2C5F8A] hover:bg-[#234b6e] text-white text-xs font-bold px-6 py-2.5 rounded-xl transition shadow-sm cursor-pointer"
                        >
                          Approve Block
                        </button>
                        <button
                          onClick={() => handleAction(rec.id, 'REJECTED')}
                          className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-6 py-2.5 rounded-xl transition cursor-pointer"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* TAB 2: ROLLING STOCK & YARD AVAILABILITY VIEW */}
        {(activeTab === 'DASHBOARD' || activeTab === 'YARD') && (
          <section className="bg-white rounded-2xl p-6 md:p-8 shadow-sm border border-slate-200/80 mt-8">
            <h2 className="text-base font-bold text-slate-900 mb-6">
              Rolling Stock & Yard Availability (Coaching Depots)
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {mockYardAvailability.map((item) => (
                <div key={item.id} className="p-5 rounded-xl border border-slate-100 bg-[#F7F9FB]">
                  <span className="text-xs font-bold font-mono text-slate-400 block mb-1">{item.id}</span>
                  <h3 className="font-bold text-slate-800 text-sm mb-2">{item.type}</h3>
                  <p className="text-xs text-slate-600 mb-1"><strong>Depot:</strong> {item.depot}</p>
                  <p className="text-xs text-slate-600 mb-3"><strong>Turnaround:</strong> {item.nextTurnaround}</p>
                  
                  <span className={`text-[10px] font-bold px-2.5 py-1 rounded-md uppercase ${
                    item.status === 'READY' ? 'bg-emerald-100 text-emerald-700' :
                    item.status === 'OVERHAUL' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'
                  }`}>
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* TAB 3: ASSETS VIEW */}
        {activeTab === 'ASSETS' && (
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
                  {mockHighRiskAssets.map((asset) => (
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
        )}
      </main>
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
      <p className="text-xs font-bold text-slate-500 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-black text-[#2C5F8A] mt-3 tracking-tight">{value}</p>
    </div>
  );
}

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