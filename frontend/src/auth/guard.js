import { getToken } from "../utils/storage.js";

export function requireAuth() {
  const token = getToken();
  const isLoginPage = window.location.pathname.includes("login.html");

  // Only redirect if definitely not logged in
  if (!token && !isLoginPage) {
    console.warn("No token → redirecting to login");
    window.location.replace("/frontend/pages/login.html");
  }
}