export const mockSummaryStats = {
  activeTrains: 18,
  recommendedBlocks: 3,
  conflictsDetected: 2,
  highRiskAssets: 5,
};

export const mockRecommendations = [
  {
    id: "REC-101",
    section: "New Delhi – Kanpur Corridor (Km 142–148)",
    startTime: "15:10",
    endTime: "17:10",
    departments: ["Engineering", "TRD"],
    affectedTrainsCount: 1,
    expectedDelayMinutes: 4,
    impactLevel: "LOW",
    status: "RECOMMENDED",
    reason: "Track tamping + OHE catenary inspection",
    affectedTrainsList: [
      { trainNo: "12627", name: "Karnataka Express", scheduledTime: "15:40", potentialDelay: "4 mins" }
    ]
  },
  {
    id: "REC-102",
    section: "Ghaziabad – Tundla Junction (Km 88–95)",
    startTime: "02:00",
    endTime: "05:30",
    departments: ["S&T"],
    affectedTrainsCount: 3,
    expectedDelayMinutes: 18,
    impactLevel: "HIGH",
    status: "RECOMMENDED",
    reason: "Signal interlocking relay replacement",
    affectedTrainsList: [
      { trainNo: "12402", name: "Magadh Express", scheduledTime: "02:45", potentialDelay: "12 mins" },
      { trainNo: "22436", name: "Vande Bharat Express", scheduledTime: "04:15", potentialDelay: "6 mins" }
    ]
  }
];

export const mockHighRiskAssets = [
  { id: "TRK_001", type: "Track Segment", location: "Km 145 (DN Line)", riskScore: 0.89, priority: "CRITICAL", department: "Engineering" },
  { id: "OHE_304", type: "Overhead Catenary", location: "Km 142 (UP Line)", riskScore: 0.78, priority: "HIGH", department: "TRD" },
  { id: "SIG_012", type: "Signal Interlocking", location: "Km 148 Junction", riskScore: 0.65, priority: "MEDIUM", department: "S&T" },
  { id: "TRK_088", type: "Turnout Switch", location: "Km 89 Switch 4B", riskScore: 0.92, priority: "CRITICAL", department: "Engineering" },
];