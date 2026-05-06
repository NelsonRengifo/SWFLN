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

  // FLATPICKR INIT
  const startPicker = flatpickr("#startMonth", {
    dateFormat: "Y-m",
    altInput: true,
    altFormat: "F Y",
    allowInput: false,
    plugins: [new monthSelectPlugin({ shorthand: true })]
  });

  const endPicker = flatpickr("#endMonth", {
    dateFormat: "Y-m",
    altInput: true,
    altFormat: "F Y",
    allowInput: false,
    plugins: [new monthSelectPlugin({ shorthand: true })]
  });

  startPicker.input.placeholder = "Select start month";
  endPicker.input.placeholder = "Select end month";

  // TAB SWITCHING
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      activeTab = tab.dataset.type;

      if (dateFilters) {
        dateFilters.style.display =
          activeTab === "free-items" ? "none" : "flex";
      }

      loadReport();
    });
  });

  // LOAD REPORT
  loadBtn?.addEventListener("click", loadReport);

  async function loadReport() {
    const limit = parseInt(document.getElementById("limit")?.value) || 10;

    const formatMonth = (picker) => {
      if (!picker.selectedDates.length) return null;

      const date = picker.selectedDates[0];
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");

      return `${year}-${month}-01`;
    };
    const today = new Date();

    const defaultStart = `${today.getFullYear()}-01-01`;
    const defaultEnd = `${today.getFullYear()}-12-31`;

    const startDate = formatMonth(startPicker) || defaultStart;
    const endDate = formatMonth(endPicker) || defaultEnd;

    reportContent.innerHTML = "<p>Loading...</p>";

    try {
      let data;

      switch (activeTab) {
        case "tutorials":
          data = await fetchTopTutorials(limit, startDate, endDate);
          renderTable(data?.data || data, "Top Tutorials");
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
          data = await fetchTopItems(limit, startDate, endDate);
          renderTable(data?.data || data, "Top Items");
          break;

        case "orgs":
          data = await fetchTopOrganizations(limit, startDate, endDate);
          renderTable(data?.data || data, "Top Organizations");
          break;

        case "free-items":
          data = await fetchFreeItems();

          const rows = data?.data || [];
          const limited = rows.slice(0, limit);

          renderTable(limited, "Free Items (Cost = $0)", {
            total: rows.length,
            showTotal: true
          });
          break;

        default:
          reportContent.innerHTML = "<p>Invalid report</p>";
      }

    } catch (err) {
      console.error(err);
      showToast("Failed to load report");
    }
  }

  // TABLE RENDER
  function renderTable(data, title = "", options = {}) {
    if (!data?.length) {
      reportContent.innerHTML = "<p>No data found</p>";
      return;
    }

    const { total = null, showTotal = false } = options;

    const headers = Object.keys(data[0]).filter(h => h !== "user_id");

    const formatHeader = (h) =>
      h.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

    reportContent.innerHTML = `
      <h2 style="margin-bottom:10px;">${title}</h2>

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

  function renderEventsTable(res) {
    if (!res?.data?.length) {
      reportContent.innerHTML = "<p>No data</p>";
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
          ${res.data.map(r => `
            <tr>
              <td>${r.event_type}</td>
              <td>${r.total}</td>
            </tr>
          `).join("")}
          <tr class="total-row">
            <td>TOTAL</td>
            <td>${res.total}</td>
          </tr>
        </tbody>
      </table>
    `;
  }

  function renderViewsTable(res) {
    if (!res?.data?.length) {
      reportContent.innerHTML = "<p>No data</p>";
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
          ${res.data.map(r => `
            <tr>
              <td>${formatMonthDisplay(r.date)}</td>
              <td>${r.views}</td>
            </tr>
          `).join("")}
          <tr class="total-row">
            <td>TOTAL</td>
            <td>${res.total}</td>
          </tr>
        </tbody>
      </table>
    `;
  }

  function formatMonthDisplay(dateStr) {
    const [year, month] = dateStr.split("-");
    const date = new Date(Number(year), Number(month) - 1);
    return date.toLocaleString("default", {
      month: "short",
      year: "numeric"
    });
  }
});