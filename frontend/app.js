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

function renderTable(data){
    const tbody = document.querySelector("#reportTable tbody");
    tbody.innerHTML = "";

    data
        .filter(row => row.count !== 0)
        .forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${row.name}</td>
                <td>${row.count}</td>
            `;
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