import { requireAuth } from "../auth/guard.js";
import { apiFetch } from "../api/fetch.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();
  // =========================
  // UPDATE PASSWORD
  // =========================
  const passwordBtn = document.getElementById("updatePasswordBtn");

  if (passwordBtn) {
    passwordBtn.onclick = async () => {
      const current_password = document.getElementById("currentPassword").value;
      const new_password = document.getElementById("newPassword").value;

      if (!current_password || !new_password) {
        return showToast("Please fill all fields");
      }

      if (current_password === new_password) {
        return showToast("New password must be different");
      }

      try {
        await apiFetch("/auth/update/password", {
          method: "POST",
          body: JSON.stringify({ current_password, new_password })
        });

        showToast("Password updated");

        document.getElementById("currentPassword").value = "";
        document.getElementById("newPassword").value = "";

      } catch (err) {
        showToast(err.message || err.detail || "Failed to update password");
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

      if (!new_username) {
        return showToast("Username cannot be empty");
      }

      try {
        await apiFetch("/auth/update/username", {
          method: "POST",
          body: JSON.stringify({ new_username })
        });

        showToast("Username updated");

        document.getElementById("newUsername").value = "";

      } catch (err) {
        showToast(err.message || err.detail || "Failed to update username");
      }
    };
  }

});