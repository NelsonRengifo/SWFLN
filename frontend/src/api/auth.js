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