import { resetPassword } from "../api/auth.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

const form = document.getElementById("resetForm");

const tokenInput = document.getElementById("token");
const newPasswordInput = document.getElementById("newPassword");
const confirmPasswordInput = document.getElementById("confirmPassword");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const reset_token = tokenInput.value.trim();
  const new_password = newPasswordInput.value.trim();
  const confirm_password = confirmPasswordInput.value.trim();

  if (!reset_token || !new_password || !confirm_password) {
    showToast("All fields are required");
    return;
  }

  if (new_password !== confirm_password) {
    showToast("Passwords do not match");
    return;
  }

  try {

    await resetPassword(reset_token, new_password, confirm_password);

    showToast("Password reset successful");

    setTimeout(() => {
      window.location.href = "/frontend/pages/login.html";
    }, 1500);

  } catch (err) {

    console.error(err);
    showToast(err.message || "Reset failed");

  }
});