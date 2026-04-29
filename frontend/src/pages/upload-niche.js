import { requireAuth } from "../auth/guard.js";
import { uploadCSV } from "../api/admin.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";
import { fetchFiles, deleteFiles } from "../api/admin.js";

requireAuth();

document.addEventListener("DOMContentLoaded", () => {
  loadSidebar();
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");
  const statusMsg = document.getElementById("statusMsg");
  const loadFilesBtn = document.getElementById("loadFilesBtn");
  const deleteBtn = document.getElementById("deleteBtn");
  const tableContainer = document.getElementById("filesTable");

  let currentFiles = [];

  if (uploadBtn) {
    uploadBtn.addEventListener("click", async () => {

      const file = fileInput.files[0];

      if (!file) {
        showToast("Please select a CSV file");
        return;
      }

      try {
        statusMsg.textContent = "Uploading...";
        await uploadCSV(file, "niche");

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

  function renderTable(data) {
    if (!Array.isArray(data) || data.length === 0) {
      tableContainer.innerHTML = "<p>No files found</p>";
      return;
    }

    console.log("RENDER TABLE DATA:", data);

    const headers = Object.keys(data[0] || {});

    function formatHeader(header) {
      return header
        .replace(/_/g, " ")           
        .replace(/\b\w/g, c => c.toUpperCase());
    }

    if (!tableContainer) {
      console.error("filesTable container not found in DOM");
    }

    tableContainer.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Select</th>
            ${headers.map(h => `<th>${formatHeader(h)}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${data.map(row => `
            <tr>
              <td>
                <input type="checkbox" value="${row.uploaded_file_id || row.id}" />
              </td>
              ${headers.map(h => `<td>${row[h] ?? ""}</td>`).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  if (loadFilesBtn) {
    loadFilesBtn.addEventListener("click", async () => {

      tableContainer.innerHTML = "Loading...";

      try {
        const response = await fetchFiles("niche", 1);
        console.log("FILES RESPONSE:", response);

        const files = response?.files || response?.data || [];

        currentFiles = files;

        renderTable(files);

      } catch (err) {
        console.error(err);
        showToast("Failed to load files");
      }
    });
  }

  function getSelectedFiles() {
    const checkboxes = tableContainer.querySelectorAll("input[type='checkbox']:checked");
    return Array.from(checkboxes).map(cb => cb.value);
  }

  if (deleteBtn) {
    deleteBtn.addEventListener("click", async () => {

      const selected = getSelectedFiles();

      if (selected.length === 0) {
        showToast("No files selected");
        return;
      }

      try {
        await deleteFiles(selected);

        showToast("Files deleted");

        loadFilesBtn.click(); // refresh

      } catch (err) {
        console.error(err);
        showToast("Delete failed");
      }
    });
  }
});