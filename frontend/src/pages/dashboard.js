// Dashboard Logic
import { requireAuth } from "../auth/guard.js";
import { fetchReport } from "../api/reports.js";
import { logout } from "../api/auth.js";

// Ensure user is authenticated
requireAuth();

// UI elements
const cards = document.querySelectorAll(".card");
const reportSection = document.getElementById("reportSection");
const reportTitle = document.getElementById("reportTitle");
const reportContent = document.getElementById("reportContent");
const logoutBtn = document.getElementById("logoutBtn");

// Card click handler
cards.forEach(card => {
  card.addEventListener("click", async () => {
    const reportType = card.dataset.report;

    reportTitle.textContent = `Loading ${reportType} report...`;
    reportContent.innerHTML = "";
    reportSection.classList.remove("hidden");

    try {
      const data = await fetchReport(reportType);
      renderReport(reportType, data);
    } catch (err) {
      reportContent.innerHTML = `<p class="error">Failed to load report.</p>`;
      console.error(err);
    }
  });
});

// Logout
logoutBtn.addEventListener("click", () => {
  logout();
});

// Render logic (simple + extensible)
function renderReport(type, data) {
  reportTitle.textContent = formatTitle(type);

  if (!data || data.length === 0) {
    reportContent.innerHTML = "<p>No data available.</p>";
    return;
  }

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  // Table headers
  const headers = Object.keys(data[0]);
  thead.innerHTML = `
    <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
  `;

  // Table rows
  data.forEach(row => {
    const tr = document.createElement("tr");
    headers.forEach(h => {
      const td = document.createElement("td");
      td.textContent = row[h] ?? "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  reportContent.innerHTML = "";
  reportContent.appendChild(table);
}

function formatTitle(type) {
  return type.charAt(0).toUpperCase() + type.slice(1) + " Report";
}
