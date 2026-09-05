const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchJson(endpoint) {
  const response = await fetch(`${BASE_URL}${endpoint}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${endpoint}`);
  }

  return response.json();
}

function formatTime(dateTime) {
  if (!dateTime) return "";

  const date = new Date(dateTime);

  if (Number.isNaN(date.getTime())) return dateTime;

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function getImpactLevel(delay) {
  if (delay >= 15) return "HIGH";
  if (delay >= 5) return "MEDIUM";
  return "LOW";
}

export async function getDashboardData() {
  const [blocks, assets, trains] = await Promise.all([
    fetchJson("/api/blocks/"),
    fetchJson("/api/assets/"),
    fetchJson("/api/trains/"),
  ]);

  const recommendedBlocks = blocks.filter(
    (block) => block.status === "RECOMMENDED"
  );

  const activeBlocks = blocks.filter((block) =>
    ["RECOMMENDED", "APPROVED", "ACTIVE", "SCHEDULED"].includes(
      block.status
    )
  );

  const recommendations = recommendedBlocks.map((block) => ({
    id: block.id,
    section: block.section,
    startTime: formatTime(block.start_time),
    endTime: formatTime(block.end_time),
    departments: block.departments
      ? block.departments.split(",").map((d) => d.trim())
      : [],
    affectedTrainsCount: block.affected_trains,
    expectedDelayMinutes: block.expected_delay_minutes,
    impactLevel: getImpactLevel(block.expected_delay_minutes),
    status: block.status,
    reason: block.reason,
    affectedTrainsList: [],
  }));

  const highRiskAssets = [...assets]
    .filter((asset) => asset.risk_score != null)
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 5)
    .map((asset) => ({
      id: asset.asset_code,
      type: asset.asset_type,
      location: asset.section,
      riskScore: asset.risk_score,
      priority: asset.priority || "LOW",
      department: "Engineering",
    }));

  return {
    summaryStats: {
      activeTrains: trains.length,
      recommendedBlocks: recommendedBlocks.length,
      conflictsDetected: 0,
      highRiskAssets: highRiskAssets.length,
    },

    recommendations,

    highRiskAssets,

    activeBlocks,
  };
}

export async function updateBlockStatus(blockId, action) {
  console.log("Updating block:", blockId, action);

  const response = await fetch(
    `${BASE_URL}/api/blocks/${blockId}/${action}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    console.error("Block update failed:", response.status, errorText);
    throw new Error(
      `Failed to ${action} block: ${response.status} ${errorText}`
    );
  }

  return response.json();
}