import { getToken, clearToken } from "../utils/storage.js";
import { showToast } from "../utils/toast.js";

const API_BASE = "http://127.0.0.1:8000";

export async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const isFormData = options.body && options.body instanceof FormData;

  const headers = {
    ...(options.headers || {}),
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };

  let res;

  try {
    res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

  } catch (err) {
    showToast("Network error. Is backend running?");
    throw err;
  }

  // ===============================
  // 401 → session expired
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

    throw new Error("Unauthorized");
  }

  // ===============================
  // Handle errors
  // ===============================
  if (!res.ok) {
    let message = "API error";

    try {
      const data = await res.json();

      // FastAPI HTTPException detail
      if (typeof data.detail === "string") {
        message = data.detail;

      // Validation errors
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map(err => err.msg)
          .join(", ");

      // Fallback generic message
      } else if (data.message) {
        message = data.message;
      }

    } catch {
      try {
        const text = await res.text();
        message = text || message;
      } catch {
        message = "Unknown server error";
      }
    }

    console.error("API ERROR:", endpoint, message);

    // SHOW BACKEND MESSAGE TO USER
    showToast(message);

    throw new Error(message);
  }

  // ===============================
  // 204 No Content
  // ===============================
  if (res.status === 204) {
    return null;
  }

  // ===============================
  // JSON safe parse
  // ===============================
  const contentType = res.headers.get("content-type");

  if (contentType && contentType.includes("application/json")) {
    return res.json();
  }

  return null;
}