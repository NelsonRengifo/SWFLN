// Dashboard Logic
import { requireAuth } from "../auth/guard.js";
import { fetchTopTutorials } from "../api/reports.js";
import {
  uploadCSV,
  fetchUploadHistory,
  fetchIngestionStatus,
  fetchTransformStatus,
  fetchProcessingLogs
} from "../api/admin.js";
import { logout } from "../api/auth.js";

// =================================
// AUTH GUARD
// =================================
requireAuth();

// =================================
// UI ELEMENTS
// =================================
const loadTutorialsBtn = document.getElementById("loadTutorialsBtn");
const reportSection = document.getElementById("reportSection");
const reportTitle = document.getElementById("reportTitle");
const reportContent = document.getElementById("reportContent");

const logoutBtn = document.getElementById("logoutBtn");

const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("csvFile");
const sourceSelect = document.getElementById("source");

const loadUploadsBtn = document.getElementById("loadUploadsBtn");
const loadIngestionBtn = document.getElementById("loadIngestionBtn");
const loadTransformsBtn = document.getElementById("loadTransformsBtn");
const loadLogsBtn = document.getElementById("loadLogsBtn");

// =================================
// LOAD TOP TUTORIALS
// =================================
if (loadTutorialsBtn) {
  loadTutorialsBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading Top Tutorials...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchTopTutorials();
      renderReport("Top Tutorials", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load report.</p>`;

    }

  });
}

// =================================
// FILE UPLOAD
// =================================
if (uploadBtn) {
  uploadBtn.addEventListener("click", async () => {

    const file = fileInput.files[0];
    const source = sourceSelect.value;

    if (!file) {
      showToast("Please select a CSV file");
      return;
    }

    try {

      await uploadCSV(file, source);
      showToast("Upload successful");

    } catch (err) {

      console.error(err);
      showToast("Upload failed");

    }

  });
}

// =================================
// LOAD UPLOAD HISTORY
// =================================
if (loadUploadsBtn) {
  loadUploadsBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading Upload History...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchUploadHistory();
      renderReport("Upload History", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load upload history.</p>`;

    }

  });
}

// =================================
// LOAD INGESTION STATUS
// =================================
if (loadIngestionBtn) {
  loadIngestionBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading Ingestion Status...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchIngestionStatus();
      renderReport("Ingestion Status", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load ingestion status.</p>`;

    }

  });
}

// =================================
// LOAD TRANSFORM STATUS
// =================================
if (loadTransformsBtn) {
  loadTransformsBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading Transform Status...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchTransformStatus();
      renderReport("Transform Status", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load transform status.</p>`;

    }

  });
}

// =================================
// LOAD FILE PROCESSING LOGS
// =================================
if (loadLogsBtn) {
  loadLogsBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading File Processing Logs...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchProcessingLogs();
      renderReport("File Processing Logs", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load logs.</p>`;

    }

  });
}

// =================================
// LOGOUT
// =================================
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    logout();
  });
}

// =================================
// TABLE RENDERER
// =================================
function renderReport(title, data) {

  reportTitle.textContent = title;

  if (!data || data.length === 0) {
    reportContent.innerHTML = "<p>No data available.</p>";
    return;
  }

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  const headers = Object.keys(data[0]);

  thead.innerHTML = `
    <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
  `;

  data.forEach(row => {

    const tr = document.createElement("tr");

    headers.forEach(h => {

      const td = document.createElement("td");
      td.textContent = row[h] ?? "";

      tr.appendChild(td);

    });

    tbody.appendChild(tr);

  });

  table.appendChild(thead);
  table.appendChild(tbody);

  reportContent.innerHTML = "";
  reportContent.appendChild(table);

}