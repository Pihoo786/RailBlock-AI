const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getTrainBlocks(trainNumber) {
  const res = await fetch(`${BASE_URL}/api/passenger/trains/${trainNumber}`);
  if (res.status === 404) return { trainNotFound: true };
  if (!res.ok) throw new Error("Failed to fetch train status");
  return res.json();
}

export async function getAllBlocks() {
  const res = await fetch(`${BASE_URL}/api/passenger/blocks`);
  if (!res.ok) throw new Error("Failed to fetch affected trains");
  return res.json();
}