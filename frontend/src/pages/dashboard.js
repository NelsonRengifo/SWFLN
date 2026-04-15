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

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();

  const logoutBtn = document.getElementById("logoutBtn");

  function getLast365DaysRange() {
    const today = new Date().toISOString().split("T")[0];
    const past = new Date();
    past.setDate(past.getDate() - 365);

    return {
      start: past.toISOString().split("T")[0],
      end: today
    };
  }

  async function loadDashboard() {
    try {
      const { start, end } = getLast365DaysRange();

      const tutorials = await fetchTopTutorials(5);
      renderTable("tutorialsTable", tutorials?.data || tutorials);

      const items = await fetchTopItems(5);
      renderTable("itemsTable", items?.data || items);

      const orgs = await fetchTopOrganizations(5);
      renderTable("orgsTable", orgs?.data || orgs);

      const views = await fetchTutorialViews(start, end);
      renderSingleValue("viewsTable", views?.total, "Total Views");

      const events = await fetchTotalEvents();
      renderSingleValue("eventsTable", events?.total, "Total Events");

    } catch (err) {
      console.error(err);
      showToast("Failed to load dashboard");
    }
  }

  function renderTable(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!data || data.length === 0) {
      container.innerHTML = "<p>No data available</p>";
      return;
    }

    const headers = Object.keys(data[0]);

    container.innerHTML = `
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

  function renderSingleValue(containerId, value, label) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <table>
        <thead>
          <tr><th>${label}</th></tr>
        </thead>
        <tbody>
          <tr><td>${value ?? 0}</td></tr>
        </tbody>
      </table>
    `;
  }

  loadDashboard();

  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }
});