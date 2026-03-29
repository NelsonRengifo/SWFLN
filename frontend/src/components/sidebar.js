// Sidebar
export function loadSidebar() {
  const sidebar = document.getElementById("sidebar");

  if (!sidebar) return;

  const path = window.location.pathname;

  const isActive = (page) => path.includes(page) ? "active" : "";

  sidebar.innerHTML = `
    <aside class="sidebar">

      <a href="dashboard.html" class="sidebar-icon ${isActive("dashboard")}" data-label="Dashboard">🏠</a>

      <a href="upload-libcal.html" class="sidebar-icon ${isActive("libcal")}" data-label="LibCal Upload">📤</a>

      <a href="upload-niche.html" class="sidebar-icon ${isActive("niche")}" data-label="Niche Upload">📁</a>

      <a href="upload-myturn.html" class="sidebar-icon ${isActive("myturn")}" data-label="MyTurn Upload">📦</a>

      <a href="reports.html" class="sidebar-icon ${isActive("reports")}" data-label="Reports">📊</a>

      <a href="settings.html" class="sidebar-icon ${isActive("settings")}" data-label="Settings">⚙️</a>

      <a href="register.html" class="sidebar-icon ${isActive("register")}" data-label="Register User">👤</a>

    </aside>
  `;
}