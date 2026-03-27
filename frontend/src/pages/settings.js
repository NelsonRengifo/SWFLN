import { requireAuth } from "../auth/guard.js";
import { apiFetch } from "../api/fetch.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {

  loadSidebar("settings");

  // =========================
  // UPDATE PASSWORD
  // =========================
  const passwordBtn = document.getElementById("updatePasswordBtn");

  if (passwordBtn) {
    passwordBtn.onclick = async () => {

      const current_password = document.getElementById("currentPassword").value;
      const new_password = document.getElementById("newPassword").value;

      try {
        await apiFetch("/auth/update/password", {
          method: "POST",
          body: JSON.stringify({ current_password, new_password })
        });

        showToast("Password updated");

      } catch (err) {
        showToast(err.message);
      }
    };
  }

  // =========================
  // UPDATE USERNAME
  // =========================
  const usernameBtn = document.getElementById("updateUsernameBtn");

  if (usernameBtn) {
    usernameBtn.onclick = async () => {

      const new_username = document.getElementById("newUsername").value;

      try {
        await apiFetch("/auth/update/username", {
          method: "POST",
          body: JSON.stringify({ new_username })
        });

        showToast("Username updated");

      } catch (err) {
        showToast(err.message);
      }
    };
  }

});