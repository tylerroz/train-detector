document.addEventListener("DOMContentLoaded", () => {

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
                statusDiv.className = "status active";
                body.classList.add("train-present");
                statusCard.classList.add("train-present");
            } else {
                statusDiv.textContent = "✅ No current train detected...";
                statusDiv.className = "status clear";
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
                    <td>${row.start_time}</td>
                    <td>${row.end_time || "-"}</td>
                    <td>${row.duration_seconds || "-"}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error(err);
        }
    }

    // --- Fetch Trains Per Day Chart ---
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

    fetchActive();
    setInterval(fetchActive, 10000);

    fetchRecentTrains();
    setInterval(fetchRecentTrains, 10000);

    renderDowChart();
});
