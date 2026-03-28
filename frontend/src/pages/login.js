import { login } from "../api/auth.js";
import { getToken } from "../utils/storage.js";
import { forgotUsername } from "../api/auth.js";

if (getToken()) {
  window.location.href = "/frontend/pages/dashboard.html";
}

const form = document.getElementById("loginForm");
const errorMsg = document.getElementById("errorMsg");
const submitBtn = form.querySelector("button[type='submit']");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  errorMsg.classList.add("hidden");

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  submitBtn.disabled = true;
  submitBtn.dataset.originalText = submitBtn.textContent;
  submitBtn.textContent = "Logging in...";
  submitBtn.classList.add("loading");

  try {
    await login(username, password);

    window.location.href = "/frontend/pages/dashboard.html";

  } catch (err) {
    errorMsg.textContent = err.message || "Login failed";
    errorMsg.classList.remove("hidden");

  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = submitBtn.dataset.originalText;
    submitBtn.classList.remove("loading");
  }
});

forgotUsernameLink.addEventListener("click", async (e) => {
  e.preventDefault();

  const email = prompt("Enter your email:");

  if (!email) return;

  try {
    await forgotUsername(email);
    alert("If an account exists, your username has been sent.");
  } catch (err) {
    alert(err.message);
  }
});