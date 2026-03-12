// Site Logic
const params = new URLSearchParams(window.location.search);
const reportType = params.get("type");

const titleMap = {
    events: "Event Attendance Report",
    training: "Training Participation Report",
    checkouts: "Equipment Checkout Report"
};

if(reportType){
    document.getElementById("report-title").textContent = titleMap[reportType] || "Report";
}

document.getElementById("loadDataBtn")?.addEventListener("click", loadReport);
document.getElementById("exportBtn")?.addEventListener("click", exportCSV);

function loadReport(){
    const month = document.getElementById("monthFilter").value;

    // Mock API Call
    fetch(`/api/reports?type=${reportType}&month=${month}`)
        .then(res => res.json())
        .then(data => renderTable(data))
        .catch(() => {
            // Mock Data
            renderTable([
                {name: "Example Item A", count: 42},
                {name: "Example Item B", count: 17}
            ]);
        });
}

function renderTable(apiResponse){
  const table = document.getElementById("reportTable");
  const thead = table.querySelector("thead");
  const tbody = table.querySelector("tbody");

  thead.innerHTML = "";
  tbody.innerHTML = "";

  // Header
  const headerRow = document.createElement("tr");
  apiResponse.columns.forEach(col => {
    const th = document.createElement("th");
    th.textContent = col.replace("_", " ").toUpperCase();
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  // Rows
  apiResponse.rows
    .filter(row => Object.values(row).every(v => v !== 0))
    .forEach(row => {
      const tr = document.createElement("tr");
      apiResponse.columns.forEach(col => {
        const td = document.createElement("td");
        td.textContent = row[col];
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
}


function exportCSV(){
    const rows = [...document.querySelectorAll("table tr")];
    const csv = rows.map(row => [...row.children].map(cell => `"${cell.textContent}"`).join(",")).join("\n");

    const blob = new Blob([csv], {type: "text/csv"});
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "report.csv";
    a.click();

    URL.revokeObjectURL(url);
}