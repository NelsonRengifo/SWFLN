import { requireAuth } from "../auth/guard.js";
import { uploadCSV } from "../api/admin.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {

  loadSidebar("libcal");

  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const statusMsg = document.getElementById("statusMsg");

  if (uploadBtn) {
    uploadBtn.addEventListener("click", async () => {

      const file = fileInput.files[0];

      if (!file) {
        showToast("Please select a CSV file");
        return;
      }

      try {
        statusMsg.textContent = "Uploading...";
        await uploadCSV(file, "libcal");

        showToast("Upload successful");
        statusMsg.textContent = "Processing...";

        setTimeout(() => statusMsg.textContent = "Ingestion complete", 2000);
        setTimeout(() => statusMsg.textContent = "Transform complete", 4000);

      } catch (err) {
        console.error(err);
        showToast("Upload failed");
        statusMsg.textContent = "Upload failed";
      }

    });
  }

});