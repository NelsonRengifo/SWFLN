// Sidebar
export function loadSidebar(activePage = "") {
  const sidebar = document.getElementById("sidebar");

  if (!sidebar) return;

  sidebar.innerHTML = `
    <aside class="sidebar">

      <a href="dashboard.html" class="sidebar-icon ${activePage === "dashboard" ? "active" : ""}" data-label="Dashboard">🏠</a>

      <a href="upload-libcal.html" class="sidebar-icon ${activePage === "libcal" ? "active" : ""}" data-label="LibCal Upload">📤</a>

      <a href="upload-niche.html" class="sidebar-icon ${activePage === "niche" ? "active" : ""}" data-label="Niche Upload">📁</a>

      <a href="upload-myturn.html" class="sidebar-icon ${activePage === "myturn" ? "active" : ""}" data-label="MyTurn Upload">📦</a>

      <a href="reports.html" class="sidebar-icon ${activePage === "reports" ? "active" : ""}" data-label="Reports">📊</a>

      <button id="openSettings" class="sidebar-icon" data-label="Settings">⚙️</button>

      <a href="register.html" class="sidebar-icon ${activePage === "register" ? "active" : ""}" data-label="Register User">👤</a>

    </aside>
  `;
}