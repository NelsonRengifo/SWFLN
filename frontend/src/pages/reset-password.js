import { resetPassword } from "../api/auth.js";
import { showToast } from "../utils/toast.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resetForm");

  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  const newPasswordInput = document.getElementById("newPassword");
  const confirmPasswordInput = document.getElementById("confirmPassword");

  if (!token) {
    showToast("Invalid or missing reset token");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const new_password = newPasswordInput.value.trim();
    const confirm_password = confirmPasswordInput.value.trim();

    if (!new_password || !confirm_password) {
      showToast("All fields are required");
      return;
    }

    if (new_password !== confirm_password) {
      showToast("Passwords do not match");
      return;
    }

    try {
      await resetPassword(token, new_password, confirm_password);

      showToast("Password reset successful");

      setTimeout(() => {
        window.location.href = "/frontend/pages/login.html";
      }, 1500);

    } catch (err) {
      console.error(err);
      showToast(err.message || "Reset failed");
    }
  });
});