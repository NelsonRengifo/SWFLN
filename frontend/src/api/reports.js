import { apiFetch } from "./fetch.js";

// =================================
// TOP TUTORIALS REPORT
// =================================
export async function fetchTopTutorials(limit = 10, startDate = null, endDate = null) {

  let endpoint = `/admin/tutorials/top?limit=${limit}`;

  if (startDate) endpoint += `&start_date=${startDate}`;
  if (endDate) endpoint += `&end_date=${endDate}`;

  const res = await apiFetch(endpoint);

  if (!res.ok) {
    throw new Error("Failed to fetch top tutorials");
  }

  return res.json();
}