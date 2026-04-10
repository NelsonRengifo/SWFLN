import { requireAuth } from "../auth/guard.js";
import {
  fetchTopTutorials,
  fetchTutorialViews,
  fetchTotalEvents,
  fetchTopItems,
  fetchTopOrganizations
} from "../api/reports.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();

  const loadBtn = document.getElementById("loadReportBtn");
  const reportContent = document.getElementById("reportContent");
  const tabs = document.querySelectorAll(".tab");

  let activeTab = "tutorials";

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeTab = tab.dataset.type;
    });
  });

  if (loadBtn) {
    loadBtn.addEventListener("click", loadReport);
  }

  async function loadReport() {
    const limit = parseInt(document.getElementById("limit").value) || 10;
    const startDate = document.getElementById("startDate").value || null;
    const endDate = document.getElementById("endDate").value || null;

    reportContent.innerHTML = "<p>Loading...</p>";

    try {
      let data;

      switch (activeTab) {
        case "tutorials":
          data = await fetchTopTutorials(limit, startDate, endDate);
          renderTable(data?.data || data);
          break;

        case "views":
          data = await fetchTutorialViews(startDate, endDate);
          renderSingleMetric(data);
          break;

        case "events":
          data = await fetchTotalEvents(startDate, endDate);
          renderSingleMetric(data);
          break;

        case "items":
          data = await fetchTopItems(limit, startDate, endDate);
          renderTable(data?.data || data);
          break;

        case "orgs":
          data = await fetchTopOrganizations(limit, startDate, endDate);
          renderTable(data?.data || data);
          break;

        default:
          reportContent.innerHTML = "<p>Invalid report type</p>";
      }

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

    reportContent.innerHTML = `
      <table>
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
      </table>
    `;
  }

  function renderSingleMetric(data) {
    reportContent.innerHTML = `
      <div class="metric-card">
        <h3>Total</h3>
        <p>${data?.total ?? 0}</p>
      </div>
    `;
  }
});