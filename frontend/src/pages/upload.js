// ======================================================
// IMPORTS
// ======================================================

import {
  uploadCSV,
  fetchUploadHistory,
  fetchProcessingLogs,
  fetchTransformStatus,
  fetchIngestionStatus
} from "../api/admin.js";

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

    fileInput.value = "";

    loadUploadHistory();

  } catch (err) {

    console.error(err);
    showToast("Upload failed");

  } finally {

    uploadBtn.disabled = false;
    uploadBtn.textContent = "Upload File";

  }
}


// ======================================================
// LOAD UPLOAD HISTORY
// ======================================================

async function loadUploadHistory() {

  try {

    const uploads = await fetchUploadHistory();

    if (!uploads || uploads.length === 0) {
      uploadHistoryContainer.innerHTML = "<p>No uploads found</p>";
      return;
    }

    const rows = uploads.map(upload => `
      <tr>
        <td>${upload.filename}</td>
        <td>${upload.source}</td>
        <td>${upload.status}</td>
        <td>${upload.created_at}</td>
      </tr>
    `).join("");

    uploadHistoryContainer.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Source</th>
            <th>Status</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;

  } catch (err) {

    console.error(err);
    uploadHistoryContainer.innerHTML = "<p>Failed to load uploads</p>";

  }

}


// ======================================================
// LOAD PROCESSING LOGS
// ======================================================

async function loadProcessingLogs() {

  try {

    const logs = await fetchProcessingLogs();

    logsContainer.innerHTML = logs.map(log => `
      <div class="log-item">
        ${log.message}
      </div>
    `).join("");

  } catch (err) {

    console.error(err);
    logsContainer.innerHTML = "<p>Failed to load logs</p>";

  }

}


// ======================================================
// LOAD TRANSFORM STATUS
// ======================================================

async function loadTransformStatus() {

  try {

    const transforms = await fetchTransformStatus();

    transformContainer.innerHTML = transforms.map(t => `
      <div>
        ${t.name} : ${t.status}
      </div>
    `).join("");

  } catch (err) {

    console.error(err);
    transformContainer.innerHTML = "<p>Failed to load transform status</p>";

  }

}


// ======================================================
// LOAD INGESTION STATUS
// ======================================================

async function loadIngestionStatus() {

  try {

    const ingestion = await fetchIngestionStatus();

    ingestionContainer.innerHTML = ingestion.map(i => `
      <div>
        ${i.source} : ${i.status}
      </div>
    `).join("");

  } catch (err) {

    console.error(err);
    ingestionContainer.innerHTML = "<p>Failed to load ingestion status</p>";

  }

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