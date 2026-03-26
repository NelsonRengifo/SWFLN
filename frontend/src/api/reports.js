import { apiFetch } from "./fetch.js";

// =================================
// TOP TUTORIALS
// GET /admin/tutorials/top
// =================================
export async function fetchTopTutorials(limit = 10, startDate = null, endDate = null) {

  let endpoint = `/admin/tutorials/top?limit=${limit}`;

  if (startDate) endpoint += `&start_date=${startDate}`;
  if (endDate) endpoint += `&end_date=${endDate}`;

  return apiFetch(endpoint);
}


// =================================
// TUTORIAL VIEWS (TOTAL)
// GET /admin/tutorials/views
// =================================
export async function fetchTutorialViews(startDate, endDate) {

  let endpoint = `/admin/tutorials/views?start_date=${startDate}&end_date=${endDate}`;

  return apiFetch(endpoint);
}


// =================================
// TOTAL EVENTS
// GET /admin/events/total
// =================================
export async function fetchTotalEvents(startDate = null, endDate = null) {

  let endpoint = `/admin/events/total`;

  if (startDate) endpoint += `?start_date=${startDate}`;
  if (endDate) endpoint += `${startDate ? "&" : "?"}end_date=${endDate}`;

  return apiFetch(endpoint);
}


// =================================
// TOP ITEMS
// GET /admin/top/items
// =================================
export async function fetchTopItems(limit = 10) {

  return apiFetch(`/admin/top/items?limit=${limit}`);
}


// =================================
// TOP ORGANIZATIONS
// GET /admin/top/organizations
// =================================
export async function fetchTopOrganizations(limit = 5) {

  return apiFetch(`/admin/top/organizations?limit=${limit}`);
}


// =================================
// GET FILE LIST (for deletion UI)
// GET /admin/files
// =================================
export async function fetchFilesBySource(source, page = 1) {

  return apiFetch(`/admin/files?source=${source}&page=${page}`);
}


// =================================
// DELETE FILES
// DELETE /admin/delete/files
// =================================
export async function deleteFiles(fileIds) {

  return apiFetch("/admin/delete/files", {
    method: "DELETE",
    body: JSON.stringify({ files: fileIds })
  });
}