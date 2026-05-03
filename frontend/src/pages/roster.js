import { requireAuth } from "../auth/guard.js";
import { fetchEventRoster } from "../api/reports.js";
import { loadSidebar } from "../components/sidebar.js";
import { showToast } from "../utils/toast.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();

  const rosterContent = document.getElementById("rosterContent");

  let filters = {
    month: "",
    attendance: ""
  };

  let currentPage = 1;
  let hasNext = false;

  const applyBtn = document.getElementById("applyFiltersBtn");
  if (applyBtn) {
    applyBtn.onclick = () => {
      filters.month = document.getElementById("monthFilter").value;
      filters.attendance = document.getElementById("attendanceFilter").value;

      currentPage = 1;
      loadRoster();
    };
  }

  document.getElementById("resetFiltersBtn").onclick = () => {
    document.getElementById("monthFilter").value = "";
    document.getElementById("attendanceFilter").value = "";

    filters = { month: "", attendance: "" };
    currentPage = 1;
    loadRoster();
  };

  async function loadRoster() {
    rosterContent.innerHTML = "<p>Loading...</p>";

    try {
      const response = await fetchEventRoster(currentPage, filters);

      if (!response?.data?.length) {
        rosterContent.innerHTML = "<p>No data found</p>";
        return;
      }

      hasNext = !!response.has_next;

      const data = response.data;
      const headers = Object.keys(data[0]).filter(h => h !== "user_id");

      function formatHeader(header) {
        return header
          .replace(/_/g, " ")
          .replace(/\b\w/g, c => c.toUpperCase());
      }

      rosterContent.innerHTML = `
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

        <div class="pagination" style="margin-top:15px; display:flex; gap:10px; align-items:center;">
          <button id="prevPage" ${currentPage === 1 ? "disabled" : ""}>Prev</button>
          <span>
            Page ${currentPage} ${hasNext ? "(More available)" : "(End)"}
          </span>
          <button id="nextPage" ${!hasNext ? "disabled" : ""}>Next</button>
        </div>
      `;

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
      console.error(err);
      showToast("Failed to load roster");
    }
  }

  loadRoster();
});