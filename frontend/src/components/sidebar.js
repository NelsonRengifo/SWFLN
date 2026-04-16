// Sidebar
import { logout } from "../api/auth.js";

export function loadSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  const path = window.location.pathname;
  const isActive = (page) => path.includes(page) ? "active" : "";

  sidebar.innerHTML = `
    <nav class="top-nav">

        <span class="logo">SWFLN Dashboard</span>
        <div class="nav-links">
        <a href="dashboard.html" class="${isActive("dashboard")}">Dashboard</a>
        <a href="reports.html" class="${isActive("reports")}">Reports</a>
        <a href="settings.html" class="${isActive("settings")}">Settings</a>
        <a href="register.html" class="${isActive("register")}">Register</a>

        <div class="dropdown">
          <button class="dropbtn">Uploads ▾</button>
          <div class="dropdown-content">
            <a href="upload-libcal.html">LibCal</a>
            <a href="upload-niche.html">Niche</a>
            <a href="upload-myturn.html">MyTurn</a>
          </div>
        </div>
      </div>

      <div class="nav-right">
        <button id="logoutBtn">Logout</button>
      </div>

    </nav>
  `;

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }
}