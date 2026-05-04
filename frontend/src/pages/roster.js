import { requireAuth } from "../auth/guard.js";
import { fetchEventRoster } from "../api/reports.js";
import { loadSidebar } from "../components/sidebar.js";
import { showToast } from "../utils/toast.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();

  // 1. Elements & State
  const rosterContent = document.getElementById("rosterContent");
  const applyBtn = document.getElementById("applyFiltersBtn");
  const resetBtn = document.getElementById("resetFiltersBtn");
  const attendanceFilter = document.getElementById("attendanceFilter");

  let filters = { startMonth: null, endMonth: null, attendance: "" };
  let currentPage = 1;
  let totalPages = 1;
  let hasNext = false;

  // 2. Helper: Format Date to YYYY-MM-01
  const getFormattedMonth = (picker) => {
    if (!picker || !picker.selectedDates.length) return null;
    const d = picker.selectedDates[0];
    const month = String(d.getMonth() + 1).padStart(2, "0");
    return `${d.getFullYear()}-${month}-01`;
  };

  // 3. Flatpickr Configuration
  const fpConfig = {
    dateFormat: "Y-m",
    altInput: true,
    altFormat: "F Y",
    allowInput: false,
    plugins: [new monthSelectPlugin({ shorthand: true })]
  };

  const startEl = document.getElementById("startMonth");
  const endEl = document.getElementById("endMonth");

  // NOTE: Ensure startEl and endEl are <input> tags in your HTML, not <select>
  const startPicker = startEl ? flatpickr(startEl, {
    ...fpConfig,
    onReady: (sd, ds, instance) => {
        if (instance.altInput) instance.altInput.placeholder = "Select start month";
    }
  }) : null;

  const endPicker = endEl ? flatpickr(endEl, {
    ...fpConfig,
    onReady: (sd, ds, instance) => {
        if (instance.altInput) instance.altInput.placeholder = "Select end month";
    }
  }) : null;

  // 4. Load Roster Logic
  async function loadRoster() {
    if (!rosterContent) return;
    rosterContent.innerHTML = "<p>Loading...</p>";

    try {
      const response = await fetchEventRoster(currentPage, filters);

      if (!response?.data?.length) {
        rosterContent.innerHTML = "<p>No data found</p>";
        return;
      }

      hasNext = response.has_next;
      totalPages = response.total_pages;

      // Extract headers excluding user_id
      const headers = Object.keys(response.data[0]).filter(h => h !== "user_id");
      const formatHeader = (h) => h.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

      rosterContent.innerHTML = `
        <table>
          <thead>
            <tr>${headers.map(h => `<th>${formatHeader(h)}</th>`).join("")}</tr>
          </thead>
          <tbody>
            ${response.data.map(row => `
              <tr>${headers.map(h => `<td>${row[h] ?? ""}</td>`).join("")}</tr>
            `).join("")}
          </tbody>
        </table>

        <div class="pagination" style="margin-top:15px; display:flex; gap:10px; align-items:center;">
          <button id="prevPage" ${currentPage === 1 ? "disabled" : ""}>Prev</button>
          <span>Page ${currentPage} of ${totalPages}</span>
          <button id="nextPage" ${!hasNext ? "disabled" : ""}>Next</button>
        </div>
      `;

      // Pagination Listeners
      const prevBtn = document.getElementById("prevPage");
      const nextBtn = document.getElementById("nextPage");

      if (prevBtn) prevBtn.onclick = () => { if (currentPage > 1) { currentPage--; loadRoster(); } };
      if (nextBtn) nextBtn.onclick = () => { if (hasNext) { currentPage++; loadRoster(); } };

    } catch (err) {
      console.error("Roster Error:", err);
      showToast("Failed to load roster");
      rosterContent.innerHTML = "<p>Error loading data.</p>";
    }
  }

  // 5. Event Handlers
  if (applyBtn) {
    applyBtn.onclick = () => {
      filters.startMonth = getFormattedMonth(startPicker);
      filters.endMonth = getFormattedMonth(endPicker);
      filters.attendance = attendanceFilter?.value || "";
      currentPage = 1;
      loadRoster();
    };
  }

  if (resetBtn) {
    resetBtn.onclick = () => {
      startPicker?.clear();
      endPicker?.clear();
      if (attendanceFilter) attendanceFilter.value = "";
      filters = { startMonth: null, endMonth: null, attendance: "" };
      currentPage = 1;
      loadRoster();
    };
  }

  // Initial Load
  loadRoster();
});
