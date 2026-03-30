import { requireAuth } from "../auth/guard.js";
import { fetchTopTutorials } from "../api/reports.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();
  const loadBtn = document.getElementById("loadReportBtn");
  const reportContent = document.getElementById("reportContent");

  if (loadBtn) {
    loadBtn.addEventListener("click", loadReport);
  }

  async function loadReport() {

    const limit = parseInt(document.getElementById("limit").value) || 10;
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;

    reportContent.innerHTML = "Loading...";

    try {

      const data = await fetchTopTutorials(
        limit,
        startDate || null,
        endDate || null
      );

      renderTable(data);

    } catch (err) {

      console.error(err);
      showToast("Failed to load report");

    }

  }

  function renderTable(data) {
    if (!data || data.length === 0) {
      reportContent.innerHTML = "<p>No data found</p>";
      return;
    }

    const headers = Object.keys(data[0]);

    const table = document.createElement("table");

    table.innerHTML = `
      <thead>
        <tr>
          ${headers.map(h => `<th>${h}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
        ${data.map(row => `
          <tr>
            ${headers.map(h => `<td>${row[h] ?? ""}</td>`).join("")}
          </tr>
        `).join("")}
      </tbody>
    `;

    reportContent.innerHTML = "";
    reportContent.appendChild(table);

  }
});