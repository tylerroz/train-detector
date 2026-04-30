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

    // --- Live train timer ---
    let timerInterval = null;
    let timerStartMs = null;

    function startTimer(startTimeStr) {
        // Server sends UTC like "2026-04-29 23:45:12" — convert to ms epoch.
        const isoStart = startTimeStr.replace(' ', 'T') + 'Z';
        const newStartMs = new Date(isoStart).getTime();

        // If the timer is already running for this same train, leave it.
        if (timerInterval && timerStartMs === newStartMs) return;

        timerStartMs = newStartMs;
        const timerEl = document.getElementById('train-timer');
        timerEl.hidden = false;

        function tick() {
            const elapsed = Math.max(0, Math.floor((Date.now() - timerStartMs) / 1000));
            const mins = Math.floor(elapsed / 60);
            const secs = elapsed % 60;
            timerEl.textContent =
                `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        tick();
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(tick, 1000);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        timerStartMs = null;
        const timerEl = document.getElementById('train-timer');
        timerEl.hidden = true;
        timerEl.textContent = '';
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
                if (data.start_time) startTimer(data.start_time);
            } else {
                statusDiv.textContent = "☹️ No current train detected...";
                body.classList.remove("train-present");
                statusCard.classList.remove("train-present");
                stopTimer();
            }
        } catch (err) {
            console.error(err);
        }
    }

    // --- Fetch Recent Trains ---
    async function fetchRecentTrains() {
        try {
            const res = await fetch("/api/recent_trains?validStatus=true");
            if (!res.ok) throw new Error("Failed to fetch /api/recent_trains");
            const rows = await res.json();

            const tbody = document.getElementById("recentTrains").querySelector("tbody");
            tbody.innerHTML = "";

            rows.forEach(row => {
                const tr = document.createElement("tr");
                if (row.status === "active" || row.active) tr.classList.add("active");
                tr.innerHTML = `
                    <td>${formatLocalTime(row.start_time)}</td>
                    <td>${formatLocalTime(row.end_time)}</td>
                    <td>${formatDuration(row.duration_seconds)}</td>
                    <td>${row.direction || "-"}</td>
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

    // MJPEG Video Player using hidden img
    const canvas = document.getElementById('videoCanvas');
    const ctx = canvas.getContext('2d');
    const hiddenImg = document.getElementById('hiddenImg');
    // Set src with timestamp to prevent caching
    hiddenImg.src = "/video?" + Date.now();
    let drawInterval;
    // Initial loading text
    ctx.fillStyle = 'white';
    ctx.font = '20px Arial';
    ctx.fillText('Loading video...', 10, 50);
    hiddenImg.onload = () => {
        if (hiddenImg.naturalWidth > 0) {
            canvas.width = hiddenImg.naturalWidth;
            canvas.height = hiddenImg.naturalHeight;
            // Start drawing once the image has loaded
            drawInterval = setInterval(() => {
                ctx.drawImage(hiddenImg, 0, 0, canvas.width, canvas.height);
            }, 50); // Update at ~20fps
        }
    };
    hiddenImg.onerror = () => {
        ctx.fillText('Video load error, retrying...', 10, 50);
        // Reload on error to handle connection issues
        setTimeout(() => {
            hiddenImg.src = "/video?" + Date.now();
        }, 1000);
    };
});
