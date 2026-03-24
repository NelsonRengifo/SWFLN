import { forgotPassword } from "../api/auth.js";
import { showToast } from "../utils/toast.js";

const form = document.getElementById("forgotForm");
const emailInput = document.getElementById("email");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = emailInput.value.trim();

  if (!email) {
    showToast("Please enter your email");
    return;
  }

  try {

    await forgotPassword(email);

    // 🔐 Always show same message (security)
    showToast("If an account exists, a reset link has been sent");

    emailInput.value = "";

  } catch (err) {

    console.error(err);
    showToast("Something went wrong");

  }
});