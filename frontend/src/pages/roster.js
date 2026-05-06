import { requireAuth } from "../auth/guard.js";
import { fetchEventRoster } from "../api/reports.js";
import { loadSidebar } from "../components/sidebar.js";
import { showToast } from "../utils/toast.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();

  // ELEMENTS
  const rosterContent = document.getElementById("rosterContent");
  const applyBtn = document.getElementById("applyFiltersBtn");
  const resetBtn = document.getElementById("resetFiltersBtn");
  const attendanceFilter = document.getElementById("attendanceFilter");

  // STATE
  let filters = {
    start_date: null,
    end_date: null,
    attendance: ""
  };

  let currentPage = 1;
  let totalPages = 1;
  let hasNext = false;

  const getFormattedMonth = (picker) => {
    if (!picker || !picker.selectedDates.length) return null;

    const d = picker.selectedDates[0];
    const month = String(d.getMonth() + 1).padStart(2, "0");

    return `${d.getFullYear()}-${month}-01`;
  };

  // FLATPICKR INIT
  const fpConfig = {
    dateFormat: "Y-m",
    altInput: true,
    altFormat: "F Y",
    allowInput: false,
    plugins: [new monthSelectPlugin({ shorthand: true })]
  };

  const startPicker = flatpickr("#startMonth", {
    ...fpConfig,
    onReady: (_, __, instance) => {
      if (instance.altInput) {
        instance.altInput.placeholder = "Select start month";
      }
    }
  });

  const endPicker = flatpickr("#endMonth", {
    ...fpConfig,
    onReady: (_, __, instance) => {
      if (instance.altInput) {
        instance.altInput.placeholder = "Select end month";
      }
    }
  });

  // LOAD ROSTER
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

      const headers = Object.keys(response.data[0]).filter(h => h !== "user_id");

      const formatHeader = (h) =>
        h.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

      rosterContent.innerHTML = `
        <table>
          <thead>
            <tr>
              ${headers.map(h => `<th>${formatHeader(h)}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${response.data.map(row => `
              <tr>
                ${headers.map(h => `<td>${row[h] ?? ""}</td>`).join("")}
              </tr>
            `).join("")}
          </tbody>
        </table>

        <div class="pagination" style="margin-top:15px; display:flex; gap:10px; align-items:center;">
          <button id="prevPage" ${currentPage === 1 ? "disabled" : ""}>Prev</button>
          <span>Page ${currentPage} of ${totalPages}</span>
          <button id="nextPage" ${!hasNext ? "disabled" : ""}>Next</button>
        </div>
      `;

      // Pagination
      document.getElementById("prevPage").onclick = () => {
        if (currentPage > 1) {
          currentPage--;
          loadRoster();
        }
      };

      document.getElementById("nextPage").onclick = () => {
        if (hasNext) {
          currentPage++;
          loadRoster();
        }
      };

    } catch (err) {
      console.error("Roster Error:", err);
      showToast("Failed to load roster");
      rosterContent.innerHTML = "<p>Error loading data.</p>";
    }
  }

  // APPLY FILTERS
  applyBtn.onclick = () => {
    filters.start_date = getFormattedMonth(startPicker);
    filters.end_date = getFormattedMonth(endPicker);

    filters.attended = attendanceFilter.value; 

    currentPage = 1;
    loadRoster();
  };

  // RESET FILTERS
  resetBtn?.addEventListener("click", () => {
    startPicker.clear();
    endPicker.clear();

    if (attendanceFilter) {
      attendanceFilter.value = "";
    }

    filters = {
      start_date: null,
      end_date: null,
      attendance: ""
    };

    currentPage = 1;
    loadRoster();
  });

  // INITIAL LOAD
  loadRoster();
});