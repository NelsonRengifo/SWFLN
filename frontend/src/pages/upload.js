// ======================================================
// IMPORTS
// ======================================================

import { uploadCSV } from "../api/admin.js";
import { showToast } from "../utils/toast.js";

// ======================================================
// DOM ELEMENTS
// ======================================================

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("csvFile");
const sourceSelect = document.getElementById("source");

const uploadHistoryContainer = document.getElementById("uploadHistory");
const logsContainer = document.getElementById("processingLogs");
const transformContainer = document.getElementById("transformStatus");
const ingestionContainer = document.getElementById("ingestionStatus");

// ======================================================
// QUICK CSV UPLOAD
// ======================================================

async function handleUpload() {

  const file = fileInput.files[0];
  const source = sourceSelect.value;

  if (!file) {
    showToast("Please select a CSV file");
    return;
  }

  try {

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";

    await uploadCSV(file, source);

    showToast("Upload successful");

    // ✨ Simulated pipeline feedback
    setTimeout(() => showToast("Ingestion complete"), 2000);
    setTimeout(() => showToast("Transform complete"), 4000);

    fileInput.value = "";

  } catch (err) {

    console.error(err);
    showToast("Upload failed");

  } finally {

    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload File";

  }
}

// ======================================================
// STATIC PLACEHOLDERS (NO BACKEND SUPPORT)
// ======================================================

function loadUploadHistory() {
  uploadHistoryContainer.innerHTML = "<p>Upload history coming soon</p>";
}

function loadProcessingLogs() {
  logsContainer.innerHTML = "<p>Logs coming soon</p>";
}

function loadTransformStatus() {
  transformContainer.innerHTML = "<p>Transform status coming soon</p>";
}

function loadIngestionStatus() {
  ingestionContainer.innerHTML = "<p>Ingestion status coming soon</p>";
}

// ======================================================
// INITIALIZE PAGE
// ======================================================

function init() {

  if (uploadBtn) {
    uploadBtn.addEventListener("click", handleUpload);
  }

  loadUploadHistory();
  loadProcessingLogs();
  loadTransformStatus();
  loadIngestionStatus();

}

init();