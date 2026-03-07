import { getToken } from "../utils/storage.js";

export function requireAuth() {
  if (!getToken()) {
    window.location.href = "/pages/login.html";
  }
}
