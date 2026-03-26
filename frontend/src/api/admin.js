import { apiFetch } from "./fetch.js";

// =================================
// UPLOAD CSV
// =================================
export async function uploadCSV(file, source) {

  const formData = new FormData();
  formData.append("file", file);
  formData.append("source", source);

  return apiFetch("/admin/upload", {
    method: "POST",
    body: formData
  });
}

// =================================
// GET FILES (FOR DELETE UI)
// =================================
export async function fetchFiles(source, page = 1) {
  return apiFetch(`/admin/files?source=${source}&page=${page}`);
}

// =================================
// DELETE FILES
// =================================
export async function deleteFiles(files) {
  return apiFetch(`/admin/delete/files`, {
    method: "DELETE",
    body: JSON.stringify({ files })
  });
}