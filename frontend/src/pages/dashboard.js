import { requireAuth } from "../auth/guard.js";
import { logout } from "../api/auth.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";
import {
  fetchTopTutorials,
  fetchTutorialViews,
  fetchTotalEvents,
  fetchTopItems,
  fetchTopOrganizations
} from "../api/reports.js";

// =====================
// INIT
// =====================
requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();
  // =====================
  // ELEMENTS
  // =====================
  const logoutBtn = document.getElementById("logoutBtn");
  const reportContent = document.getElementById("reportContent");

  // =====================
  // DATE RANGE
  // =====================
  function getLast30DaysRange() {
    const today = new Date().toISOString().split("T")[0];

    const past = new Date();
    past.setDate(past.getDate() - 30);

    return {
      start: past.toISOString().split("T")[0],
      end: today
    };
  }

  // =====================
  // LOAD DASHBOARD
  // =====================
  async function loadDashboard() {
    try {
      const { start, end } = getLast30DaysRange();

      // ---- Top Tutorials ----
      const tutorials = await fetchTopTutorials(10, start, end);
      renderTable(tutorials);

      // ---- Metrics ----
      const views = await fetchTutorialViews(start, end);
      document.getElementById("viewsMetric").textContent =
        views?.total_views || 0;

      const events = await fetchTotalEvents(start, end);
      document.getElementById("eventsMetric").textContent =
        events?.total_events || 0;

      const items = await fetchTopItems(5);
      document.getElementById("itemsMetric").textContent =
        items?.[0]?.item_name || "—";

      const orgs = await fetchTopOrganizations(5);
      document.getElementById("orgsMetric").textContent =
        orgs?.[0]?.organization_name || "—";

    } catch (err) {
      console.error(err);
      showToast("Failed to load dashboard");
    }
  }

  loadDashboard();

  // =====================
  // TABLE RENDER
  // =====================
  function renderTable(data) {
    if (!data || data.length === 0) {
      reportContent.innerHTML = "<p>No data available.</p>";
      return;
    }

    const headers = Object.keys(data[0]);

    reportContent.innerHTML = `
      <table>
        <thead>
          <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
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

  // =====================
  // LOGOUT
  // =====================
  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }

});