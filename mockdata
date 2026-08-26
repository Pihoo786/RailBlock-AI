export const mockSummaryStats = {
  activeTrains: 14,
  recommendedBlocks: 3,
  conflictsDetected: 2,
  highRiskAssets: 5,
};

export const mockRecommendations = [
  {
    id: "REC-101",
    section: "New Delhi - Kanpur Section (Km 142-148)",
    startTime: "15:10",
    endTime: "17:10",
    departments: ["Engineering", "TRD"],
    affectedTrainsCount: 1,
    expectedDelayMinutes: 4,
    impactLevel: "LOW", // LOW, MEDIUM, HIGH
    status: "RECOMMENDED", // RECOMMENDED, APPROVED, REJECTED
    affectedTrainsList: [
      { trainNo: "12627", name: "Karnataka Express", scheduledTime: "15:40", potentialDelay: "4 mins" }
    ]
  }
];

export const mockHighRiskAssets = [
  { id: "TRK_001", type: "Track Segment", location: "Km 145", riskScore: 0.89, priority: "HIGH", department: "Engineering" },
  { id: "OHE_304", type: "Overhead Equipment", location: "Km 142", riskScore: 0.78, priority: "HIGH", department: "TRD" },
  { id: "SIG_012", type: "Signal Interlocking", location: "Km 148", riskScore: 0.65, priority: "MEDIUM", department: "S&T" },
];
