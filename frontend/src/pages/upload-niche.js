import { requireAuth } from "../auth/guard.js"; 
import { uploadCSV, fetchFiles, deleteFiles } from "../api/admin.js";
import { showToast } from "../utils/toast.js";
import { loadSidebar } from "../components/sidebar.js";

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
  let currentPage = 1;
  let totalPages = 1;
  let hasNext = false;

  // UPLOAD
  uploadBtn?.addEventListener("click", async () => {
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

  // LOAD FILES
  async function loadFiles(page = 1) {
    tableContainer.innerHTML = "Loading...";

    try {
      const response = await fetchFiles("niche", page);

      const files = response?.files || response?.data || [];

      currentFiles = files;
      currentPage = response?.page || page;
      totalPages = response?.total_pages || 1;
      hasNext = response?.has_next || false;

      renderTable(files);

    } catch (err) {
      console.error(err);
      showToast("Failed to load files");
    }
  }

  loadFilesBtn?.addEventListener("click", () => {
    currentPage = 1;
    loadFiles(currentPage);
  });

  // TABLE
  function renderTable(data) {
    if (!Array.isArray(data) || data.length === 0) {
      tableContainer.innerHTML = "<p>No files found</p>";
      return;
    }

    const headers = Object.keys(data[0]);

    const formatHeader = (h) =>
      h.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

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
              <td><input type="checkbox" value="${row.uploaded_file_id || row.id}" /></td>
              ${headers.map(h => `<td>${row[h] ?? ""}</td>`).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>

      <div class="pagination" style="margin-top:15px; display:flex; gap:10px;">
        <button id="prevPage" ${currentPage === 1 ? "disabled" : ""}>Prev</button>
        <span>Page ${currentPage} of ${totalPages}</span>
        <button id="nextPage" ${!hasNext ? "disabled" : ""}>Next</button>
      </div>
    `;

    document.getElementById("prevPage").onclick = () => {
      if (currentPage > 1) loadFiles(--currentPage);
    };

    document.getElementById("nextPage").onclick = () => {
      if (hasNext) loadFiles(++currentPage);
    };
  }

  // DELETE
  function getSelectedFiles() {
    return Array.from(
      tableContainer.querySelectorAll("input[type='checkbox']:checked")
    ).map(cb => cb.value);
  }

  deleteBtn?.addEventListener("click", async () => {
    const selected = getSelectedFiles();

    if (!selected.length) {
      showToast("No files selected");
      return;
    }

    try {
      await deleteFiles(selected);
      showToast("Files deleted");
      loadFiles(currentPage);
    } catch (err) {
      console.error(err);
      showToast("Delete failed");
    }
  });
});