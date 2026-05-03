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
  const dateFilters = document.getElementById("dateFilters");

  let activeTab = "tutorials";

  // TAB SWITCHING
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeTab = tab.dataset.type;

      // Hide date filters for free items
      if (dateFilters) {
        dateFilters.style.display =
          activeTab === "free-items" ? "none" : "flex";
      }
    });
  });

  // LOAD REPORT
  if (loadBtn) {
    loadBtn.addEventListener("click", loadReport);
  }

  async function loadReport() {
    const limit = parseInt(document.getElementById("limit")?.value) || 10;

    const startMonth = document.getElementById("startMonth")?.value;
    const endMonth = document.getElementById("endMonth")?.value;

    const formatMonthToDate = (month) =>
      month ? `${month}-01` : null;

    const startDate = formatMonthToDate(startMonth);
    const endDate = formatMonthToDate(endMonth);

    reportContent.innerHTML = "<p>Loading...</p>";

    const setSectionTitle = (title) => {
      reportContent.innerHTML = `<h2 style="margin-bottom:10px;">${title}</h2>`;
    };

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

          const allRows = data?.data || data || [];
          const limitedRows = allRows.slice(0, limit);

          renderTable(limitedRows, {
            total: allRows.length,
            showTotal: true
          });
          break;

        default:
          reportContent.innerHTML = "<p>Invalid report type</p>";
      }

    } catch (err) {
      console.error(err);
      showToast("Failed to load report");
    }
  }

  // GENERIC TABLE
  function renderTable(data, options = {}) {
    if (!data || data.length === 0) {
      reportContent.innerHTML = "<p>No data found</p>";
      return;
    }

    const { total = null, showTotal = false } = options;

    const headers = Object.keys(data[0]).filter(h => h !== "user_id");

    const formatHeader = (header) =>
      header.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

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
          ${showTotal && total !== null ? `
            <tr class="total-row">
              <td>Total</td>
              <td colspan="${headers.length - 1}">${total}</td>
            </tr>
          ` : ""}
        </tbody>
      </table>
    `;
  }

  // EVENTS TABLE
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

  // VIEWS TABLE
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
});