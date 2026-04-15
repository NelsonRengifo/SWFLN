// Sidebar
export function loadSidebar() {
  const container = document.getElementById("sidebar");
  if (!container) return;

  const path = window.location.pathname;

  const isActive = (page) => path.includes(page) ? "active" : "";

  container.innerHTML = `
    <nav class="top-nav">

      <div class="logo">SWFLN Reporting Dashboard</div>

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

      <button id="logoutBtn" class="logout-btn">Logout</button>

    </nav>
  `;
}