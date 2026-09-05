const STORAGE_KEY = "railblock_dept_requests";

// Real backend by default
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function loadMock() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveMock(requests) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(requests));
}

export async function getRequests(departmentLabel) {
  if (USE_MOCK) {
    const all = loadMock();
    return all.filter((r) => r.department === departmentLabel);
  }

  const res = await fetch(`${BASE_URL}/api/maintenance-requests`);

  if (!res.ok) {
    throw new Error(`Failed to fetch requests: ${res.status}`);
  }

  const all = await res.json();

  return all.filter((r) => r.department === departmentLabel);
}

export async function createRequest(payload) {
  if (USE_MOCK) {
    const all = loadMock();

    const newRequest = {
      ...payload,
      id: `REQ-${Date.now()}`,
      status: "SUBMITTED",
      reported_date: new Date().toISOString(),
    };

    all.unshift(newRequest);
    saveMock(all);

    return newRequest;
  }

  const res = await fetch(`${BASE_URL}/api/maintenance-requests`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(
      `Failed to submit request: ${res.status} ${errorText}`
    );
  }

  return res.json();
}