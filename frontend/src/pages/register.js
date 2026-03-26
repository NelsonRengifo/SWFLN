import { registerUser } from "../api/auth.js";
import { showToast } from "../utils/toast.js";
import { requireAuth } from "../auth/guard.js";

// Ensure user is logged in
requireAuth();

const form = document.getElementById("registerForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    username: document.getElementById("username").value.trim(),
    email: document.getElementById("email").value.trim(),
    first_name: document.getElementById("firstName").value.trim(),
    last_name: document.getElementById("lastName").value.trim(),
    password: document.getElementById("password").value.trim(),
    user_role: document.getElementById("role").value
  };

  // Basic validation
  if (
    !payload.username ||
    !payload.email ||
    !payload.first_name ||
    !payload.last_name ||
    !payload.password ||
    !payload.user_role
  ) {
    showToast("All fields are required");
    return;
  }

  try {

    await registerUser(payload);

    showToast("User created successfully");

    form.reset();

  } catch (err) {

    console.error(err);
    showToast(err.message || "Registration failed");

  }
});