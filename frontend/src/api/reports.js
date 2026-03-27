import { apiFetch } from "./fetch.js";

// =================================
// HELPER: build query string safely
// =================================
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
export async function fetchTutorialViews(startDate, endDate) {
  const query = buildQuery({
    start_date: startDate,
    end_date: endDate
  });

  return apiFetch(`/admin/tutorials/views${query}`);
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