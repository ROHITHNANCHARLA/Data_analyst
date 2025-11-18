console.log("📊 Restored Dashboard JS Loaded");

/* Load everything on page load */
document.addEventListener("DOMContentLoaded", () => {
    loadKPIs();
    loadGraphs();
});

/* ------------------------------------------
   1️⃣ LOAD KPI SUMMARY
------------------------------------------- */
async function loadKPIs() {
    try {
        const r = await fetch("/api/summary");
        const j = await r.json();
        const s = j.summary;

        document.getElementById("k_total").innerText = s.total_records.toLocaleString();
        document.getElementById("k_avg").innerText = "₹" + s.avg_salary.toLocaleString();
        document.getElementById("k_sector").innerText = s.top_sector;
        document.getElementById("k_location").innerText = s.top_state;

    } catch (err) {
        console.error("❌ KPI Load Failed", err);
    }
}

/* ------------------------------------------
   2️⃣ LOAD ALL GRAPHS USING /api/summary
------------------------------------------- */
async function loadGraphs() {
    try {
        const r = await fetch("/api/summary");
        const j = await r.json();

        const byYear = j.by_year;
        const byState = j.by_state;
        const byCompany = j.by_company;
        const skills = j.skills_data;

        /* ---- Salary Trend (Line Chart) ---- */
        Plotly.newPlot("chart_salary_trend", [{
            x: byYear.map(x => x.Year),
            y: byYear.map(x => x.Avg_Salary),
            mode: "lines+markers",
            line: { width: 3, color: "#4db8ff" },
            marker: { size: 8 }
        }], {
            margin: { t: 25, b: 40 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { color: "#e8f6ff" }
        });

        /* ---- Top States ---- */
        Plotly.newPlot("chart_top_states", [{
            x: byState.map(x => x.Location),
            y: byState.map(x => x.Avg_Salary),
            type: "bar",
            marker: { color: "#33ccff" }
        }], {
            margin: { t: 25, b: 60 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { color: "#e8f6ff" }
        });

        /* ---- Top Companies ---- */
        Plotly.newPlot("chart_companies", [{
            x: byCompany.map(x => x.Company_Name),
            y: byCompany.map(x => x.Avg_Salary),
            type: "bar",
            marker: { color: "#a680ff" }
        }], {
            margin: { t: 25, b: 80 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { color: "#e8f6ff" }
        });

        /* ---- Skill Radar ---- */
        Plotly.newPlot("chart_skill_radar", [{
            type: "scatterpolar",
            r: skills.map(s => s.Count),
            theta: skills.map(s => s.Skill),
            fill: "toself",
            marker: { color: "#00ffcc" }
        }], {
            polar: { radialaxis: { visible: true } },
            paper_bgcolor: "rgba(0,0,0,0)",
            font: { color: "#e8f6ff" }
        });

    } catch (err) {
        console.error("❌ Graph Load Failed", err);
    }
}
