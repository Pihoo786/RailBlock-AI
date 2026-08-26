import { mockTrainResponse, mockAllBlocks } from "./mockResponses";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export async function getTrainBlocks(trainNumber) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300)); // simulate network delay
    return mockTrainResponse[trainNumber] || { trainNotFound: true };
  }
  const res = await fetch(`${BASE_URL}/api/passenger/trains/${trainNumber}`);
  if (res.status === 404) return { trainNotFound: true };
  if (!res.ok) throw new Error("Failed to fetch train status");
  return res.json();
}

export async function getAllBlocks() {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 300));
    return mockAllBlocks;
  }
  const res = await fetch(`${BASE_URL}/api/passenger/blocks`);
  if (!res.ok) throw new Error("Failed to fetch affected trains");
  return res.json();
}