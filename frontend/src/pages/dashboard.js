// Dashboard Logic
import { requireAuth } from "../auth/guard.js";
import { logout } from "../api/auth.js";
import { showToast } from "../utils/toast.js";

import {
  fetchTopTutorials,
  fetchTutorialViews,
  fetchTotalEvents,
  fetchTopItems,
  fetchTopOrganizations
} from "../api/reports.js";

// =====================
// AUTH GUARD
// =====================
requireAuth();

// =====================
// ELEMENTS
// =====================
const logoutBtn = document.getElementById("logoutBtn");
const reportContent = document.getElementById("reportContent");

const panel = document.getElementById("sidePanel");
const panelContent = document.getElementById("panelContent");
const panelTitle = document.getElementById("panelTitle");

// =====================
// DATE RANGE (LAST 30 DAYS)
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
// LOAD DASHBOARD DATA
// =====================
async function loadDashboard() {
  try {
    const { start, end } = getLast30DaysRange();

    // -----------------
    // TOP TUTORIALS TABLE
    // -----------------
    const tutorials = await fetchTopTutorials(10, start, end);
    renderTable(tutorials);

    // -----------------
    // METRICS
    // -----------------
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
// SIDEBAR PANEL CONTROL
// =====================
document.getElementById("openUploads").onclick = () => {
  openPanel("Upload Options", `
    <a href="libcal.html">LibCal Upload</a><br/><br/>
    <a href="niche.html">Niche Upload</a><br/><br/>
    <a href="myturn.html">MyTurn Upload</a>
  `);
};

document.getElementById("openSettings").onclick = () => {
  openPanel("Settings", `
    <p>Account settings coming soon...</p>
  `);
};

function openPanel(title, content) {
  panelTitle.textContent = title;
  panelContent.innerHTML = content;
  panel.classList.add("active");
}

document.getElementById("closePanel").onclick = () => {
  panel.classList.remove("active");
};

// =====================
// LOGOUT
// =====================
if (logoutBtn) {
  logoutBtn.addEventListener("click", logout);
}