const STORAGE_KEY = "railblock_dept_requests";
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

function loadMock() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); }
  catch { return []; }
}

function saveMock(requests) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(requests));
}

export async function getRequests(departmentLabel) {
  if (USE_MOCK) {
    const all = loadMock();
    return all.filter((r) => r.department === departmentLabel);
  }
  // NOTE: backend doesn't support department filtering yet (per Person 1) —
  // this fetches everything and filters client-side as a stopgap.
  const res = await fetch(`${BASE_URL}/api/maintenance-jobs/`);
  if (!res.ok) throw new Error("Failed to fetch requests");
  const all = await res.json();
  return all.filter((r) => r.department === departmentLabel);
}

export async function createRequest(payload) {
  if (USE_MOCK) {
    const all = loadMock();
    const newRequest = {
      ...payload,
      id: `REQ-${Date.now()}`,
      status: "SUBMITTED", // uppercase, matches new enum
      reported_date: new Date().toISOString(),
    };
    all.unshift(newRequest);
    saveMock(all);
    return newRequest;
  }
  const res = await fetch(`${BASE_URL}/api/maintenance-jobs/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to submit request");
  return res.json();
}