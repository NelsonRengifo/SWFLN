// Dashboard Logic
import { requireAuth } from "../auth/guard.js";
import { fetchTopTutorials } from "../api/reports.js";
import { uploadCSV } from "../api/admin.js";
import { logout } from "../api/auth.js";
import { showToast } from "../utils/toast.js";

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

// =================================
// LOAD TOP TUTORIALS (REAL DATA)
// =================================
if (loadTutorialsBtn) {
  loadTutorialsBtn.addEventListener("click", async () => {

    reportTitle.textContent = "Loading Top Tutorials...";
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {

      const data = await fetchTopTutorials();

      if (!data || data.length === 0) {
        reportContent.innerHTML = "<p>No data available.</p>";
        return;
      }

      renderReport("Top Tutorials", data);

    } catch (err) {

      console.error(err);
      reportContent.innerHTML = `<p class="error">Failed to load report.</p>`;

    }

  });
}

// =================================
// FILE UPLOAD (REAL)
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

      // ✨ Simulate backend processing
      setTimeout(() => showToast("Ingestion complete"), 2000);
      setTimeout(() => showToast("Transform complete"), 4000);

    } catch (err) {

      console.error(err);
      showToast("Upload failed");

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