document.addEventListener("DOMContentLoaded", () => {

    function formatLocalTime(timestamp) {
        if (!timestamp) return "-"; // handle null/undefined
        
        // Replace space with "T" and append "Z" to treat as UTC
        // "2026-01-24 00:45:47" → "2026-01-24T00:45:47Z"
        const isoString = timestamp.replace(' ', 'T') + 'Z';
        const date = new Date(isoString);
        
        // Options for formatting
        const options = {
            month: 'short',   // Jan, Feb, etc.
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            second: '2-digit',
            hour12: true,      // AM/PM format
            timeZone: 'America/Chicago'
        };
        
        // undefined → uses the user's local timezone
        return date.toLocaleString(undefined, options); 
    }

    function formatDuration(seconds) {
        if (seconds == null || isNaN(seconds)) return "Active!";
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    }

    // --- Fetch Train Status ---
    async function fetchActive() {
        try {
            const res = await fetch("/api/active");
            if (!res.ok) throw new Error("Failed to fetch /api/active");
            const data = await res.json();

            const statusDiv = document.getElementById("train-status");
            const body = document.body;
            const statusCard = document.getElementById("statusCard");

            if (data.active) {
                statusDiv.textContent = "🚂 Train Present!";
                body.classList.add("train-present");
                statusCard.classList.add("train-present");
            } else {
                statusDiv.textContent = "☹️ No current train detected...";
                body.classList.remove("train-present");
                statusCard.classList.remove("train-present");
            }
        } catch (err) {
            console.error(err);
        }
    }

    // --- Fetch Recent Trains ---
    async function fetchRecentTrains() {
        try {
            const res = await fetch("/api/recent_trains");
            if (!res.ok) throw new Error("Failed to fetch /api/recent_trains");
            const rows = await res.json();

            const tbody = document.getElementById("recentTrains").querySelector("tbody");
            tbody.innerHTML = "";

            rows.forEach(row => {
                const tr = document.createElement("tr");
                if (row.status === "active" || row.active) tr.classList.add("active");
                tr.innerHTML = `
                    <td>${row.status || "-"}</td>
                    <td>${formatLocalTime(row.start_time)}</td>
                    <td>${formatLocalTime(row.end_time)}</td>
                    <td>${formatDuration(row.duration_seconds)}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error(err);
        }
    }

    // --- Fetch Trains Per Day Chart ---
    // https://mariadb.com/docs/server/reference/sql-functions/date-time-functions/dayofweek
    async function fetchDowData() {
        try {
            const res = await fetch("/api/trains_per_dow");
            if (!res.ok) throw new Error("Failed to fetch /api/trains_per_dow");
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
        } catch (err) {
            console.error(err);
            return [0,0,0,0,0,0,0];
        }
    }

    let dowChartInstance = null;

    async function renderDowChart() {
        const ctx = document.getElementById("dowChart").getContext("2d");
        const dowData = await fetchDowData();
        const labels = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]; // matches 0=Sunday

        console.log("Chart labels:", labels);
        console.log("Chart data:", dowData);

        if (dowChartInstance) {
            // update existing chart
            dowChartInstance.data.datasets[0].data = dowData;
            dowChartInstance.update();
        } else {
            // first time, create the chart
            dowChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Trains per Day",
                        data: dowData,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            scaleSteps: 1
                        }
                    }
                }
            });
        }
        return dowChartInstance;
    }

    fetchActive();
    setInterval(fetchActive, 10000);

    fetchRecentTrains();
    setInterval(fetchRecentTrains, 10000);

    renderDowChart();
    setInterval(renderDowChart, 10000);
});
