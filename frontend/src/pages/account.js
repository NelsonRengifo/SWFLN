import { requireAuth } from "../auth/guard.js";
import { apiFetch } from "../api/fetch.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";
import { fetchUsers, deleteUsers } from "../api/auth.js";

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
      const confirm_password = document.getElementById("confirmPassword").value;

      if (!current_password || !new_password) {
        return showToast("Please fill all fields");
      }

      if (current_password === new_password) {
        return showToast("New password must be different");
      }

      if (new_password !== confirm_password) {
        showToast("Passwords do not match");
        return;
      }

      try {
        await apiFetch("/auth/update/password", {
          method: "POST",
          body: JSON.stringify({ current_password, new_password, confirm_password })
        });

        showToast("Password updated");

        document.getElementById("currentPassword").value = "";
        document.getElementById("newPassword").value = "";
        document.getElementById("confirmPassword").value = "";

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
      const confirm_username = document.getElementById("confirmUsername").value;

      if (!new_username) {
        return showToast("Username cannot be empty");
      }

      if (new_username !== confirm_username) {
        showToast("Usernames do not match");
        return;
      }

      try {
        await apiFetch("/auth/update/username", {
          method: "POST",
          body: JSON.stringify({ new_username, confirm_username })
        });

        showToast("Username updated");

        document.getElementById("newUsername").value = "";

      } catch (err) {
        showToast(err.message || err.detail || "Failed to update username");
      }
    };
  }

  async function loadUsers() {
    const container = document.getElementById("usersTable");
    if (!container) return;
    container.innerHTML = "<p>Loading...</p>";

    try {
      const response = await fetchUsers();
      const data = response.data;

      if (!data || data.length === 0) {
        container.innerHTML = "<p>No users found</p>";
        return;
      }

      const headers = Object.keys(data[0]).filter(h => h !== "user_id");

      function formatHeader(header) {
        return header
          .replace(/_/g, " ")
          .replace(/\b\w/g, c => c.toUpperCase());
      }

      container.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Select</th>
              ${headers.map(h => `<th>${formatHeader(h)}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${data.map(user => `
              <tr>
                <td>
                  <input type="checkbox" class="user-checkbox" value="${user.user_id}">
                </td>
                ${headers.map(h => `<td>${user[h] ?? ""}</td>`).join("")}
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;

    } catch (err) {
      console.error(err);
      showToast("Failed to load users");
    }
  }

  const deleteBtn = document.getElementById("deleteSelectedUsersBtn");

  if (deleteBtn) {
    deleteBtn.onclick = async () => {
      const checked = Array.from(document.querySelectorAll(".user-checkbox:checked"));

      if (checked.length === 0) {
        return showToast("No users selected");
      }

      const userIds = checked.map(cb => cb.value);

      if (!confirm(`Delete ${userIds.length} users?`)) return;

      try {
        await deleteUsers(userIds);

        showToast("Users deleted");

        // Refresh table
        loadUsers();

      } catch (err) {
        console.error(err);
        showToast("Failed to delete users");
      }
    };
  }

  loadUsers();
});