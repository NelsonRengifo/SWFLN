import { requireAuth } from "../auth/guard.js";
import {
  fetchTopTutorials,
  fetchTutorialViews,
  fetchTotalEvents,
  fetchTopItems,
  fetchTopOrganizations,
  fetchFreeItems
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

      const startInput = document.getElementById("startDate");
      const endInput = document.getElementById("endDate");

      if (activeTab === "free-items") {
        startInput.disabled = true;
        endInput.disabled = true;
      } else {
        startInput.disabled = false;
        endInput.disabled = false;
      }
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

    function setSectionTitle(title) {
      reportContent.innerHTML = `<h2 style="margin-bottom:10px;">${title}</h2>`;
    }

    try {
      let data;

    switch (activeTab) {
      case "tutorials":
        setSectionTitle("Top Tutorials");
        data = await fetchTopTutorials(limit, startDate, endDate);
        renderTable(data?.data || data);
        break;

      case "views":
        data = await fetchTutorialViews(startDate, endDate);
        renderViewsTable(data);
        break;

      case "events":
        data = await fetchTotalEvents(startDate, endDate);
        renderEventsTable(data);
        break;

      case "items":
        setSectionTitle("Top Items");
        data = await fetchTopItems(limit, startDate, endDate);
        renderTable(data?.data || data);
        break;

      case "orgs":
        setSectionTitle("Top Organizations");
        data = await fetchTopOrganizations(limit, startDate, endDate);
        renderTable(data?.data || data);
        break;

      case "free-items":
        setSectionTitle("Free Items (Cost = $0)");
        data = await fetchFreeItems();
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

    function formatHeader(header) {
      return header
        .replace(/_/g, " ")
        .replace(/\b\w/g, c => c.toUpperCase());
    }

    reportContent.innerHTML = `
      <table>
        <thead>
          <tr>
            ${headers.map(h => `<th>${formatHeader(h)}</th>`).join("")}
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

  function renderEventsTable(response) {
    if (!response?.data?.length) {
      reportContent.innerHTML = "<p>No data found</p>";
      return;
    }

    reportContent.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Event Type</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          ${response.data.map(row => `
            <tr>
              <td>${row.event_type}</td>
              <td>${row.total}</td>
            </tr>
          `).join("")}

          <tr class="total-row">
            <td>TOTAL</td>
            <td>${response.total}</td>
          </tr>
        </tbody>
      </table>
    `;
  }

  function renderViewsTable(response) {
    if (!response?.data?.length) {
      reportContent.innerHTML = "<p>No data found</p>";
      return;
    }

    reportContent.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Month</th>
            <th>Views</th>
          </tr>
        </thead>
        <tbody>
          ${response.data.map(row => `
            <tr>
              <td>${formatMonth(row.date)}</td>
              <td>${row.views}</td>
            </tr>
          `).join("")}

          <tr class="total-row">
            <td>TOTAL</td>
            <td>${response.total}</td>
          </tr>
        </tbody>
      </table>
    `;
  }

  function formatMonth(dateStr) {
    const [year, month] = dateStr.split("-");
    const date = new Date(Number(year), Number(month) - 1);
    return date.toLocaleString("default", {
      month: "short",
      year: "numeric"
    });
  }

  function renderSingleMetric(data) {
    reportContent.innerHTML = `
      <div class="metrics-grid">
        <div class="metric-card">
          <p>Total</p>
          <h3>${data?.total ?? 0}</h3>
        </div>
      </div>
    `;
  }
});