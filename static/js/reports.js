// static/js/reports.js
console.log("📄 reports.js loaded");

document.addEventListener("DOMContentLoaded", () => {

    if (window.location.pathname !== "/reports") {
        return;
    }

    console.log("📘 reports.js active");

    const tableBody = document.getElementById("pred_table_body");

    async function loadHistory() {
        try {
            const res = await fetch("/api/prediction_history?limit=5000");
            const data = await res.json();

            let rows = "";

            data.predictions.forEach(r => {
                rows += `
                <tr>
                    <td>${r.ts}</td>
                    <td>${r.job_title}</td>
                    <td>${r.sector}</td>
                    <td>${r.location}</td>
                    <td>${r.rating}</td>
                    <td>₹${r.predicted_salary}</td>
                    <td>₹${r.min_salary} - ₹${r.max_salary}</td>
                    <td>${r.confidence}%</td>
                    <td>${(r.recommendations || []).join(", ")}</td>
                </tr>`;
            });

            tableBody.innerHTML = rows;
        } catch (err) {
            console.error("❌ Failed loading predictions:", err);
        }
    }

    loadHistory();
});
