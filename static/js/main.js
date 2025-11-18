
console.log("🚀 DataAnalyst Insight JS Loaded Successfully");


document.addEventListener("DOMContentLoaded", () => {

  /* =======================================================
     SMART AUTO-SUGGESTION ENGINE
  ======================================================== */
  function setupSuggestions(inputId, boxId, field) {
    const input = document.getElementById(inputId);
    const box = document.getElementById(boxId);

    input.addEventListener("keyup", async () => {
      const q = input.value.trim();
      if (!q) return (box.style.display = "none");

      const res = await fetch(`/api/suggestions?q=${q}&field=${field}`);
      const suggestions = await res.json();

      if (!suggestions.length) {
        box.style.display = "none";
        return;
      }

      box.innerHTML = suggestions
        .map(item => `<div class="suggest-item">${item}</div>`)
        .join("");
      box.style.display = "block";

      document.querySelectorAll(`#${boxId} .suggest-item`).forEach(elem => {
        elem.onclick = () => {
          input.value = elem.innerText;
          box.style.display = "none";
        };
      });
    });
  }

  // Activate 3 smart suggestion fields
  setupSuggestions("yearInput", "yearSuggest", "Year");
  setupSuggestions("sectorInput", "sectorSuggest", "Sector");
  setupSuggestions("stateInput", "locationSuggest", "Location");


  /* =======================================================
     MAIN ANALYTICS ACTION
  ======================================================== */
  const applyBtn = document.getElementById("applyBtn");
  if (!applyBtn) return;

  console.log("📊 Analytics Page Active");

  applyBtn.addEventListener("click", async () => {

    const payload = {
      year: document.getElementById("yearInput").value.trim(),
      sector: document.getElementById("sectorInput").value.trim(),
      location: document.getElementById("stateInput").value.trim()
    };

    console.log("📦 Sending Filter Payload →", payload);

    applyBtn.disabled = true;
    applyBtn.innerHTML = "⏳ Loading...";
    document.body.style.cursor = "wait";

    try {
      const res = await fetch("/api/analytics_filter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      console.log("📥 Received Analytics Data:", data);

      if (!res.ok || data.error) {
        alert("⚠️ No matching data found.");
        return;
      }

      // ================= Summary Box ===============
      const summaryCard = document.getElementById("summaryCard");
      const summaryText = document.getElementById("summaryText");

      summaryCard.style.display = "block";
      summaryText.innerHTML = `
        <strong>Matched Sectors:</strong> ${data.by_sector.length} |
        <strong>Top Skill:</strong> ${data.by_skills?.[0]?.Skill || "N/A"} |
        <strong>Years Found:</strong> ${data.by_year.length}
      `;

      const safe = (arr, key) => (arr?.length ? arr.map(x => x[key]) : []);

      // ============= Charts =============
      Plotly.react("chart_sector", [{
        x: safe(data.by_sector, "Sector"),
        y: safe(data.by_sector, "Avg_Salary"),
        type: "bar",
        marker: { color: "#00eaff" }
      }], { title: "💼 Average Salary by Sector", paper_bgcolor: "transparent", font: { color: "#fff" } });

      Plotly.react("chart_skills", [{
        labels: safe(data.by_skills, "Skill"),
        values: safe(data.by_skills, "Count"),
        type: "pie",
        hole: 0.4
      }], { title: "🧠 Top Skills Demand", paper_bgcolor: "transparent", font: { color: "#fff" } });

      Plotly.react("chart_rating", [{
        x: safe(data.by_rating, "Rating"),
        y: safe(data.by_rating, "Avg_Salary"),
        mode: "markers",
        marker: { color: "#7cff7c", size: 10 }
      }], { title: "🏢 Salary vs Rating", paper_bgcolor: "transparent", font: { color: "#fff" } });

      Plotly.react("chart_year", [{
        x: safe(data.by_year, "Year"),
        y: safe(data.by_year, "Avg_Salary"),
        mode: "lines+markers",
        line: { color: "#ffd60a", width: 3 }
      }], { title: "📈 Salary Trend", paper_bgcolor: "transparent", font: { color: "#fff" } });

    } catch (err) {
      console.error("💥 Analytics Error:", err);
      alert("⚠️ Could not load analytics.");
    } finally {
      applyBtn.disabled = false;
      applyBtn.innerHTML = "🚀 Apply";
      document.body.style.cursor = "default";
    }
  });
});
