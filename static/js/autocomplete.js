// static/js/autocomplete.js

console.log("✨ Autocomplete Engine Loaded");

// Attach autocomplete to any field
function attachAutocomplete(inputId, fieldType) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Create dropdown element
    const box = document.createElement("div");
    box.className = "auto-box";
    box.style.position = "absolute";
    box.style.background = "#0b1c2c";
    box.style.width = input.offsetWidth + "px";
    box.style.maxHeight = "200px";
    box.style.overflowY = "auto";
    box.style.zIndex = 9999;
    box.style.borderRadius = "8px";
    box.style.border = "1px solid #1f4ba3";
    box.style.display = "none";
    box.style.boxShadow = "0 0 10px rgba(0,255,255,0.3)";
    input.style.position = "relative";
    input.parentElement.appendChild(box);

    input.addEventListener("input", async () => {
        const query = input.value.trim().toLowerCase();
        if (query.length === 0) {
            box.style.display = "none";
            return;
        }

        const res = await fetch(`/api/suggestions?q=${query}&field=${fieldType}`);
        const list = await res.json();

        box.innerHTML = "";
        if (!list.length) {
            box.style.display = "none";
            return;
        }

        list.forEach(item => {
            const opt = document.createElement("div");
            opt.style.padding = "8px 12px";
            opt.style.cursor = "pointer";
            opt.style.color = "#b7e9ff";

            opt.innerHTML = item;

            opt.addEventListener("mouseenter", () => {
                opt.style.background = "#154c79";
            });
            opt.addEventListener("mouseleave", () => {
                opt.style.background = "transparent";
            });

            opt.addEventListener("click", () => {
                input.value = item;
                box.style.display = "none";
            });

            box.appendChild(opt);
        });

        box.style.display = "block";
    });

    // Hide dropdown when clicking outside
    window.addEventListener("click", (e) => {
        if (!box.contains(e.target) && e.target !== input) {
            box.style.display = "none";
        }
    });
}

// Enable autocomplete for analytics page
document.addEventListener("DOMContentLoaded", () => {
    attachAutocomplete("yearInput", "Year");
    attachAutocomplete("sectorInput", "Sector");
    attachAutocomplete("stateInput", "Location");
});
