import { apiFetch } from "./fetch.js";

function buildQuery(params) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      query.append(key, value);
    }
  });

  return query.toString() ? `?${query.toString()}` : "";
}


// =================================
// TOP TUTORIALS
// =================================
export async function fetchTopTutorials(limit = 10, startDate = null, endDate = null) {
  const query = buildQuery({
    limit,
    start_date: startDate,
    end_date: endDate
  });

  return apiFetch(`/admin/tutorials/top${query}`);
}


// =================================
// TUTORIAL VIEWS
// =================================
export function fetchTutorialViews(start_date, end_date) {
  const params = new URLSearchParams();

  if (start_date) params.append("start_date", start_date);
  if (end_date) params.append("end_date", end_date);

  return apiFetch(`/admin/tutorials/views?${params.toString()}`);
}


// =================================
// TOTAL EVENTS
// =================================
export async function fetchTotalEvents(startDate = null, endDate = null) {
  const query = buildQuery({
    start_date: startDate,
    end_date: endDate
  });

  return apiFetch(`/admin/events/total${query}`);
}


// =================================
// TOP ITEMS
// =================================
export async function fetchTopItems(limit = 10) {
  return apiFetch(`/admin/top/items?limit=${limit}`);
}


// =================================
// TOP ORGANIZATIONS
// =================================
export async function fetchTopOrganizations(limit = 5) {
  return apiFetch(`/admin/top/organizations?limit=${limit}`);
}


// =================================
// FILE LIST (DELETE UI)
// =================================
export async function fetchFilesBySource(source, page = 1) {
  return apiFetch(`/admin/files?source=${source}&page=${page}`);
}


// =================================
// DELETE FILES
// =================================
export async function deleteFiles(fileIds) {
  return apiFetch("/admin/delete/files", {
    method: "DELETE",
    body: JSON.stringify({ files: fileIds })
  });
}

// =================================
// FREE ITEMS
// =================================
export async function fetchFreeItems() {
  return apiFetch("/admin/items/free", {
    method: "GET"
  });
}

// =================================
// EVENT ROSTER
// =================================
export async function fetchEventRoster(page = 1, filters = {}) {
  const params = { page };

  if (filters.start_date) params.start_date = filters.start_date;
  if (filters.end_date) params.end_date = filters.end_date;

  // ✅ already boolean or undefined — just pass it if it exists
  if (filters.attended !== undefined) {
    params.attended = filters.attended;
  }

  return apiFetch(`/admin/event/roster?${new URLSearchParams(params)}`);
}