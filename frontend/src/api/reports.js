import { apiFetch } from "./fetch.js";

const REPORT_ENDPOINTS = {
  events: "/reports/events",
  training: "/reports/training",
  checkouts: "/reports/checkouts"
};

export async function fetchReport(type) {
  const endpoint = REPORT_ENDPOINTS[type];

  if (!endpoint) {
    throw new Error(`Unknown report type: ${type}`);
  }

  const res = await apiFetch(endpoint);

  if (!res.ok) {
    throw new Error("Report fetch failed");
  }

  return res.json();
}
