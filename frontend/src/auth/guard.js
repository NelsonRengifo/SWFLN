import { getToken } from "../utils/storage.js";

export function requireAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = "/frontend/pages/login.html";
  }
}