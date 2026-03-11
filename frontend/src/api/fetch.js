import { getToken, clearToken } from "../utils/storage.js";
import { showToast } from "../utils/toast.js";

const API_BASE = "http://localhost:8000";

export async function apiFetch(endpoint, options = {}) {

  const token = getToken();

  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(options.headers || {}),
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  // ===============================
  // 401 → Token expired
  // ===============================
  if (res.status === 401) {

    const isOnLoginPage = window.location.pathname.includes("login.html");

    clearToken();

    if (!isOnLoginPage) {

      showToast("Session expired. Please login again.");

      setTimeout(() => {
        window.location.href = "/frontend/pages/login.html";
      }, 1200);

    }

    return null;

  }

  // ===============================
  // API Errors
  // ===============================
  if (!res.ok) {

    let message = "API error";

    try {

      const data = await res.json();
      message = data.detail || message;

    } catch {

      const text = await res.text();
      message = text || message;

    }

    throw new Error(message);

  }

  // ===============================
  // 204 No Content
  // ===============================
  if (res.status === 204) {
    return null;
  }

  // ===============================
  // Parse JSON safely
  // ===============================
  const contentType = res.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
    return res.json();
  }

  return null;

}