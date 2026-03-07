import { setToken, clearToken } from "../utils/storage.js";
import { apiFetch } from "./fetch.js";

const BASE_URL = "http://localhost:8000/auth";

// --------------------
// LOGIN
// --------------------
export async function login(username, password) {
  const data = await apiFetch(`${BASE_URL}/login`, {
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
import { showToast } from "./toast.js";

export async function logout() {
  try {
    await apiFetch(`${BASE_URL}/logout`, {
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
