// static/js/predictor.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("🤖 Predictor JS Active");

  const form = document.getElementById("predictForm");
  const resultCard = document.getElementById("resultCard");
  const confBar = document.getElementById("confBar");
  const confPct = document.getElementById("confPercent");
  const rangeText = document.getElementById("rangeText");
  const recoList = document.getElementById("recoList");

  // fetch autocomplete lists
  async function loadAutocomplete() {
    try {
      const res = await fetch("/api/autocomplete");
      const j = await res.json();
      const sectors = j.sectors || [];
      const skills = j.skills || [];
      const locations = j.locations || [];

      const sectorsD = document.getElementById("sectors");
      const skillsD = document.getElementById("skills_list");
      const locD = document.getElementById("locations");

      sectorsD.innerHTML = sectors.map(s => `<option value="${s}">`).join("");
      skillsD.innerHTML = skills.map(s => `<option value="${s}">`).join("");
      locD.innerHTML = locations.map(s => `<option value="${s}">`).join("");
    } catch (e) {
      console.warn("Autocomplete load failed", e);
    }
  }

  loadAutocomplete();

  // draw initial empty gauge
  function drawGauge(value = 0, min=0, max=100000) {
    const gaugeVal = Math.round(value);
    const config = [{
      type: "indicator",
      mode: "gauge+number",
      value: gaugeVal,
      domain: { x: [0, 1], y: [0, 1] },
      title: { text: "Predicted Salary (₹)", font: { size: 16 } },
      gauge: {
        axis: { range: [min, max], tickformat: ",.0f" },
        bar: { color: "#00ffd5" },
        steps: [
          { range: [min, max*0.4], color: "#ff6b6b" },
          { range: [max*0.4, max*0.75], color: "#ffd60a" },
          { range: [max*0.75, max], color: "#2dce89" }
        ],
        threshold: {
          line: { color: "black", width: 3 },
          thickness: 0.8,
          value: gaugeVal
        }
      },
      number: { valueformat: ",.0f", font: { size: 20 } }
    }];

    const layout = { margin: { t: 30, b: 10 }, paper_bgcolor: "rgba(0,0,0,0)", font: { color: "#e8f6ff" } };
    Plotly.react("gauge", config, layout, {displayModeBar:false});
  }

  // animate gauge from 0 to value
  async function animateGauge(targetValue, min = 0, max = 200000) {
    // create the gauge base once with 0
    drawGauge(min, min, max);
    // then animate to target using Plotly.animate
    const steps = 30;
    const frames = [];
    for (let i = 1; i <= steps; i++) {
      const v = min + (targetValue - min) * (i / steps);
      frames.push({
        data: [{ value: v, number: { valueformat: ",.0f" } }],
        traces: [0],
        name: `f${i}`
      });
    }
    Plotly.animate("gauge", frames, { transition: { duration: 60, easing: "cubic-in-out" }, frame: { duration: 60, redraw: true }});
  }

  // confidence bar visual (color)
  function setConfidence(pct) {
    confPct.innerText = `${pct}%`;
    confBar.style.width = `${pct}%`;
    // color: red <40, amber 40-75, green >75
    if (pct < 40) {
      confBar.className = "progress-bar bg-danger";
    } else if (pct < 75) {
      confBar.className = "progress-bar" ;
      confBar.style.background = "#ffd60a";
    } else {
      confBar.className = "progress-bar bg-success";
    }
  }

  function showRecommendations(list) {
    recoList.innerHTML = "";
    list.forEach(role => {
      const el = document.createElement("div");
      el.className = "pill";
      el.innerText = role;
      recoList.appendChild(el);
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      job_title: document.getElementById("jobTitle").value.trim(),
      sector: document.getElementById("sector").value.trim(),
      rating: parseFloat(document.getElementById("rating").value || 0),
      skills: document.getElementById("skills").value.trim(),
      location: document.getElementById("location").value.trim()
    };

    // UI feedback
    const btn = form.querySelector("button[type='submit']");
    btn.disabled = true;
    btn.innerText = "⏳ Predicting...";

    try {
      const res = await fetch("/api/predict_salary", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      const j = await res.json();
      if (!res.ok || j.error) {
        alert("⚠️ Prediction failed: " + (j.error || "server error"));
        return;
      }

      // display
      resultCard.style.display = "block";

      // choose gauge max by bucketed predicted salary to make gauge look nice
      const pred = j.predicted_salary;
      let gaugeMax = 200000;
      if (pred < 50000) gaugeMax = 100000;
      else if (pred < 100000) gaugeMax = 150000;
      else if (pred < 300000) gaugeMax = 350000;
      else gaugeMax = Math.ceil(pred * 1.5);

      // animate gauge
      await animateGauge(pred, 0, gaugeMax);

      // range text
      rangeText.innerHTML = `₹${Number(j.min_salary).toLocaleString()} — ₹${Number(j.max_salary).toLocaleString()}`;

      // confidence
      setConfidence(j.confidence || 40);

      // recommendations
      showRecommendations(j.recommendations || []);

    } catch (err) {
      console.error("Prediction error:", err);
      alert("⚠️ Could not predict. See console.");
    } finally {
      btn.disabled = false;
      btn.innerText = "🚀 Predict Salary";
    }
  });
});
