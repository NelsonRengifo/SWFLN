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
// UPLOAD HISTORY
// =================================
export async function fetchUploadHistory() {

  return apiFetch("/admin/uploads");

}

// =================================
// INGESTION STATUS
// =================================
export async function fetchIngestionStatus() {

  return apiFetch("/admin/ingestion");

}

// =================================
// TRANSFORM STATUS
// =================================
export async function fetchTransformStatus() {

  return apiFetch("/admin/transforms");

}

// =================================
// FILE PROCESSING LOGS
// =================================
export async function fetchProcessingLogs() {

  return apiFetch("/admin/logs");

}