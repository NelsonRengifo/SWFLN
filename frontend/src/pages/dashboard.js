import { requireAuth } from "../auth/guard.js";
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

  function getCurrentYearRange() {
    const now = new Date();
    const year = now.getFullYear();

    return {
      start: `${year}-01-01`,
      end: `${year}-12-31`
    };
  }

  async function loadDashboard() {
    try {
      const { start, end } = getCurrentYearRange();

      const tutorials = await fetchTopTutorials(10);
      renderTable("tutorialsTable", tutorials?.data || tutorials);

      const items = await fetchTopItems(5);
      renderTable("itemsTable", items?.data || items);

      const orgs = await fetchTopOrganizations(5);
      renderTable("orgsTable", orgs?.data || orgs);

      const views = await fetchTutorialViews(start, end);
      renderViewsTable(views);

      const events = await fetchTotalEvents();
      renderEventsTable(events);

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

  function renderEventsTable(response) {
    const container = document.getElementById("eventsTable");

    const data = response?.data || [];
    const total = response?.total || 0;

    if (!data.length) {
      container.innerHTML = "<p>No data available</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Event Type</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              <td>${row.event_type}</td>
              <td>${row.total}</td>
            </tr>
          `).join("")}

          <tr style="font-weight: 600; background:#f1f5f9;">
            <td>TOTAL</td>
            <td>${total}</td>
          </tr>

        </tbody>
      </table>
    `;
  }

  function renderViewsTable(response) {
    const container = document.getElementById("viewsTable");

    const data = response?.data || [];
    const total = response?.total || 0;

    if (!data.length) {
      container.innerHTML = "<p>No data available</p>";
      return;
    }

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Month</th>
            <th>Views</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              <td>${formatMonth(row.date)}</td>
              <td>${row.views}</td>
            </tr>
          `).join("")}

          <tr style="font-weight: 600; background:#f1f5f9;">
            <td>TOTAL</td>
            <td>${total}</td>
          </tr>

        </tbody>
      </table>
    `;
  }

  function formatMonth(dateStr) {
    const [year, month, day] = dateStr.split("-");

    const date = new Date(
      Number(year),
      Number(month) - 1,
      Number(day)
    );

    return date.toLocaleString("default", {
      month: "short",
      year: "numeric"
    });
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
});