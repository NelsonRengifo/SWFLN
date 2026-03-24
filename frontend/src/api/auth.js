import { setToken, clearToken } from "../utils/storage.js";
import { apiFetch } from "./fetch.js";
import { showToast } from "../utils/toast.js";

// --------------------
// LOGIN
// --------------------
export async function login(username, password) {

  const data = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });

  if (!data || !data.token) {
    throw new Error("Invalid credentials");
  }

  setToken(data.token);
}

// --------------------
// LOGOUT
// --------------------
export async function logout() {

  try {

    await apiFetch("/auth/logout", {
      method: "POST"
    });

    showToast("Logged out successfully 👋");

  } catch (err) {

    console.error("Logout error:", err);

  } finally {

    clearToken();

    setTimeout(() => {
      window.location.href = "/frontend/pages/login.html";
    }, 800);

  }

}

// --------------------
// FORGOT PASSWORD
// --------------------
export async function forgotPassword(email) {
  return apiFetch("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email })
  });
}

// --------------------
// RESET PASSWORD
// --------------------
export async function resetPassword(reset_token, new_password, confirm_password) {
  return apiFetch("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({
      reset_token,
      new_password,
      confirm_password
    })
  });
}

// --------------------
// UPDATE PASSWORD (Logged In)
// --------------------
export async function updatePassword(current_password, new_password, confirm_password) {
  return apiFetch("/auth/update/password", {
    method: "POST",
    body: JSON.stringify({
      current_password,
      new_password,
      confirm_password
    })
  });
}