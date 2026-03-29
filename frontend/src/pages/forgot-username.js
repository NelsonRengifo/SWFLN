import { forgotUsername } from "../api/auth.js";
import { showToast } from "../utils/toast.js";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("forgotUsernameForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;

    try {
      await forgotUsername(email);
      showToast("If email exists, username has been sent");
    } catch (err) {
      console.error(err);
      showToast("Something went wrong");
    }
  });
});