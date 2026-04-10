// Sidebar
export function loadSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  const path = window.location.pathname;
  const isActive = (page) => path.includes(page) ? "active" : "";

  const icon = (svg) => `<span class="icon">${svg}</span>`;

  sidebar.innerHTML = `
    <aside class="sidebar">

      <a href="dashboard.html" class="sidebar-icon ${isActive("dashboard")}" data-label="Dashboard">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M3 13h8V3H3v10zm10 8h8v-6h-8v6zM3 21h8v-6H3v6zm10-10h8V3h-8v8z" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="upload-libcal.html" class="sidebar-icon ${isActive("libcal")}" data-label="LibCal Upload">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="upload-niche.html" class="sidebar-icon ${isActive("niche")}" data-label="Niche Upload">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M4 4h16v16H4z" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="upload-myturn.html" class="sidebar-icon ${isActive("myturn")}" data-label="MyTurn Upload">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M12 8v4l3 3" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="reports.html" class="sidebar-icon ${isActive("reports")}" data-label="Reports">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M4 19h16M4 15h10M4 11h7M4 7h13" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="settings.html" class="sidebar-icon ${isActive("settings")}" data-label="Settings">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/><path d="M19.4 15a1.7 1.7 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.82-.33 1.7 1.7 0 0 0-1 1.54V21a2 2 0 1 1-4 0v-.09a1.7 1.7 0 0 0-1-1.54 1.7 1.7 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.7 1.7 0 0 0 .33-1.82 1.7 1.7 0 0 0-1.54-1H3a2 2 0 1 1 0-4h.09a1.7 1.7 0 0 0 1.54-1 1.7 1.7 0 0 0-.33-1.82l-.06-.06A2 2 0 1 1 7.07 3.3l.06.06a1.7 1.7 0 0 0 1.82.33h0A1.7 1.7 0 0 0 10 2.15V2a2 2 0 1 1 4 0v.15a1.7 1.7 0 0 0 1.05 1.54h0a1.7 1.7 0 0 0 1.82-.33l.06-.06A2 2 0 1 1 21 7.07l-.06.06a1.7 1.7 0 0 0-.33 1.82v0A1.7 1.7 0 0 0 21.85 10H22a2 2 0 1 1 0 4h-.15a1.7 1.7 0 0 0-1.54 1z" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

      <a href="register.html" class="sidebar-icon ${isActive("register")}" data-label="Register User">
        ${icon(`<svg viewBox="0 0 24 24" fill="none"><path d="M16 21v-2a4 4 0 0 0-8 0v2"/><circle cx="12" cy="7" r="4"/><path d="M20 8v6M23 11h-6" stroke="currentColor" stroke-width="2"/></svg>`)}
      </a>

    </aside>
  `;
}