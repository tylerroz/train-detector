async function fetchActive() {
    const res = await fetch("/api/active");
    const data = await res.json();
    const statusDiv = document.getElementById("train-status");
    if(data.active) {
        statusDiv.textContent = "🚂 Train Present!";
        statusDiv.className = "status active";
    } else {
        statusDiv.textContent = "✅ All Clear";
        statusDiv.className = "status clear";
    }
}

// Example: trains per day of week (from API)
async function fetchDowData() {
    const res = await fetch("/api/trains_per_dow");
    const data = await res.json();
    return [
        data["0"] || 0,
        data["1"] || 0,
        data["2"] || 0,
        data["3"] || 0,
        data["4"] || 0,
        data["5"] || 0,
        data["6"] || 0
    ];
}

async function renderDowChart() {
    const ctx = document.getElementById("dowChart").getContext("2d");
    const dowData = await fetchDowData();

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
            datasets: [{
                label: "Trains per Day",
                data: dowData,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

async function fetchRecentTrains() {
    const res = await fetch("/api/recent_trains");
    const rows = await res.json();

    const tbody = document.getElementById("recentTrains").querySelector("tbody");
    tbody.innerHTML = ""; // clear old rows

    rows.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.id}</td>
            <td>${row.status || "-"}</td>
            <td>${row.start_time}</td>
            <td>${row.end_time || "-"}</td>
            <td>${row.duration_seconds || "-"}</td>
        `;
        tbody.appendChild(tr);
    });
}

// initial fetch + auto-refresh
fetchActive();
setInterval(fetchActive, 10000); // update status every 5s

fetchRecentTrains();
setInterval(fetchRecentTrains, 10000);

// let's hold off on doing this
// renderDowChart();
