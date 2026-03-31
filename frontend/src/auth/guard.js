import { getToken } from "../utils/storage.js";

export function requireAuth() {
  const token = getToken();

  const isLoginPage = window.location.pathname.includes("login.html");

  if (!token && !isLoginPage) {
    window.location.href = "/frontend/pages/login.html";
    return;
  }
}