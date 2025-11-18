# app.py
from flask import Flask, render_template, jsonify, request, make_response
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pandas as pd, os, io, sqlite3, json
from datetime import datetime
from fuzzywuzzy import fuzz, process
import numpy as np

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "data_analyst_jobs.csv")
PRED_DB_PATH = os.path.join(BASE_DIR, "data", "predictions.db")  # DB file

# ---------------- Ensure data folder exists ----------------
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ---------------- SQLite helper: init DB ----------------
def init_pred_db():
    """Create predictions DB & table if missing."""
    conn = sqlite3.connect(PRED_DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            job_title TEXT,
            sector TEXT,
            rating REAL,
            location TEXT,
            skills TEXT,
            predicted_salary INTEGER,
            min_salary INTEGER,
            max_salary INTEGER,
            confidence INTEGER,
            recommendations TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_prediction_row(row: dict):
    """Insert a prediction dict into SQLite predictions table."""
    conn = sqlite3.connect(PRED_DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO predictions (
            ts, job_title, sector, rating, location, skills,
            predicted_salary, min_salary, max_salary, confidence, recommendations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row.get("ts"),
        row.get("job_title"),
        row.get("sector"),
        row.get("rating"),
        row.get("location"),
        row.get("skills"),
        int(row.get("predicted_salary")),
        int(row.get("min_salary")),
        int(row.get("max_salary")),
        int(row.get("confidence")),
        json.dumps(row.get("recommendations", []), ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

def query_predictions(limit=200, start=None, end=None, sector=None, location=None):
    """Return list of prediction rows as dicts with optional filters."""
    conn = sqlite3.connect(PRED_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    sql = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if start:
        sql += " AND ts >= ?"
        params.append(start)
    if end:
        sql += " AND ts <= ?"
        params.append(end)
    if sector:
        sql += " AND lower(sector) LIKE ?"
        params.append(f"%{sector.lower()}%")
    if location:
        sql += " AND lower(location) LIKE ?"
        params.append(f"%{location.lower()}%")

    sql += " ORDER BY ts DESC LIMIT ?"
    params.append(int(limit))

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    # parse recommendations JSON string back to list
    for r in rows:
        try:
            r["recommendations"] = json.loads(r["recommendations"]) if r.get("recommendations") else []
        except Exception:
            r["recommendations"] = []
    return rows

# initialize DB at start
init_pred_db()

# ---------------- Load and clean dataset ----------------
def load_df():
    if not os.path.exists(DATA_PATH):
        print("⚠️ Data file not found:", DATA_PATH)
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
    except Exception:
        df = pd.read_csv(DATA_PATH, encoding="latin1")

    df.columns = [c.strip() for c in df.columns]

    # Normalize numeric columns
    for col in ["Avg_Salary", "Min_Salary", "Max_Salary", "Rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Fill text fields
    for col in ["Skills", "Sector", "Location", "Company_Name"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # Derive year
    if "Date" in df.columns:
        df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year.fillna(2023).astype(int)
    elif "Year" not in df.columns:
        df["Year"] = 2023

    return df

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    print("🏠 Home Page Accessed")
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    print("📊 Dashboard Page Accessed")
    return render_template("dashboard.html")

@app.route("/analytics")
def analytics():
    print("📈 Analytics Page Accessed")
    df = load_df()
    years = sorted(df["Year"].dropna().unique().tolist()) if not df.empty else []
    sectors = sorted(df["Sector"].dropna().unique().tolist()) if not df.empty else []
    locations = sorted(df["Location"].dropna().unique().tolist()) if not df.empty else []
    return render_template("analytics.html", years=years, sectors=sectors, locations=locations)

@app.route("/reports")
def reports():
    print("📑 Reports Page Accessed")
    return render_template("reports.html")

@app.route("/predictor")
def predictor():
    print("🤖 Predictor Page Accessed")
    return render_template("predictor.html")

# ---------------- DASHBOARD SUMMARY ----------------
@app.route("/api/summary")
def api_summary():
    df = load_df()
    if df.empty:
        return jsonify({
            "summary": {
                "total_records": 0,
                "avg_salary": 0,
                "top_sector": "-",
                "top_state": "-"
            },
            "by_year": [],
            "by_state": [],
            "by_company": [],
            "skills_data": []
        })

    summary = {
        "total_records": len(df),
        "avg_salary": int(df["Avg_Salary"].mean()),
        "top_sector": df["Sector"].value_counts().idxmax() if "Sector" in df.columns and not df["Sector"].empty else "-",
        "top_state": df["Location"].value_counts().idxmax() if "Location" in df.columns and not df["Location"].empty else "-"
    }

    by_year = df.groupby("Year", as_index=False)["Avg_Salary"].mean().sort_values("Year").to_dict(orient="records")
    by_state = df.groupby("Location", as_index=False)["Avg_Salary"].mean().sort_values("Avg_Salary", ascending=False).head(10).to_dict(orient="records")
    by_company = df.groupby("Company_Name", as_index=False)["Avg_Salary"].mean().sort_values("Avg_Salary", ascending=False).head(10).to_dict(orient="records")

    skills_series = df["Skills"].astype(str).str.replace(";", ",").str.split(",").explode().str.strip()
    skills_data = skills_series.value_counts().head(8).rename_axis("Skill").reset_index(name="Count").to_dict(orient="records")

    return jsonify({
        "summary": summary,
        "by_year": by_year,
        "by_state": by_state,
        "by_company": by_company,
        "skills_data": skills_data
    })

# ---------------- ANALYTICS FILTER ----------------
@app.route("/api/analytics_filter", methods=["POST"])
def api_analytics_filter():
    payload = request.get_json() or {}

    year_in = str(payload.get("year", "")).strip().lower()
    sector_in = str(payload.get("sector", "")).strip().lower()
    location_in = str(payload.get("location", "")).strip().lower()

    print("📦 Analytics Filter Payload →", payload)

    df = load_df()
    if df.empty:
        return jsonify({"error": "Dataset unavailable"}), 404

    dff = df.copy()

    # 1) YEAR — Partial + Fuzzy
    if year_in:
        all_years = df["Year"].astype(str).unique().tolist()
        best_year = process.extractOne(year_in, all_years, scorer=fuzz.partial_ratio)
        if best_year and best_year[1] >= 60:
            year_match = best_year[0]
            print(f"🎯 Matched Year → {year_match}")
            dff = dff[dff["Year"].astype(str) == str(year_match)]
        else:
            print("⚠️ No year match → using full data")

    # 2) SECTOR — Partial + Fuzzy
    if sector_in:
        sectors = df["Sector"].astype(str).str.lower().unique().tolist()
        best_sector = process.extractOne(sector_in, sectors, scorer=fuzz.partial_ratio)
        if best_sector and best_sector[1] >= 55:
            sec_match = best_sector[0]
            print(f"🎯 Matched Sector → {sec_match}")
            dff = dff[dff["Sector"].astype(str).str.lower() == sec_match]
        else:
            print("⚠️ No sector match → using partial search")
            dff = dff[dff["Sector"].astype(str).str.lower().str.contains(sector_in, na=False)]

    # 3) LOCATION — Partial + Fuzzy
    if location_in:
        locations = df["Location"].astype(str).str.lower().unique().tolist()
        best_location = process.extractOne(location_in, locations, scorer=fuzz.partial_ratio)
        if best_location and best_location[1] >= 55:
            loc_match = best_location[0]
            print(f"🎯 Matched Location → {loc_match}")
            dff = dff[dff["Location"].astype(str).str.lower() == loc_match]
        else:
            print("⚠️ No location fuzzy match → using partial search")
            dff = dff[dff["Location"].astype(str).str.lower().str.contains(location_in, na=False)]

    print(f"🔍 Filtered {len(dff)} rows out of {len(df)}")

    # fallback: return full dataset when empty (helps UX)
    if dff.empty:
        print("⚠️ No match → Returning full dataset instead")
        dff = df.copy()

    result = {
        "by_sector": dff.groupby("Sector", as_index=False)["Avg_Salary"].mean().to_dict(orient="records"),
        "by_skills": dff["Skills"].dropna().astype(str).str.replace(";", ",").str.split(",").explode().str.strip()
                     .value_counts().head(10).rename_axis("Skill").reset_index(name="Count").to_dict(orient="records"),
        "by_rating": dff.groupby("Rating", as_index=False)["Avg_Salary"].mean().to_dict(orient="records"),
        "by_year": dff.groupby("Year", as_index=False)["Avg_Salary"].mean().to_dict(orient="records")
    }

    return jsonify(result)

# ---------------- AUTOCOMPLETE + SUGGESTIONS ----------------
@app.route("/api/autocomplete")
def api_autocomplete():
    df = load_df()
    if df.empty:
        return jsonify({"sectors": [], "skills": [], "locations": []})

    sectors = sorted(df["Sector"].dropna().astype(str).unique().tolist())
    locations = sorted(df["Location"].dropna().astype(str).unique().tolist())

    skills_series = df["Skills"].dropna().astype(str).str.replace(";", ",").str.split(",").explode().str.strip()
    skills = skills_series[skills_series != ""].value_counts().index.tolist()
    skills = skills[:200]

    return jsonify({"sectors": sectors, "skills": skills, "locations": locations})

# ---------------- PREDICTOR (improved version) ----------------
@app.route("/api/predict_salary", methods=["POST"])
def api_predict_salary():
    payload = request.get_json() or {}
    job_title = (payload.get("job_title") or "").strip()
    sector_in = (payload.get("sector") or "").strip()
    rating = float(payload.get("rating") or 0)
    location = (payload.get("location") or "").strip()
    skills_in = (payload.get("skills") or "").strip()

    df = load_df()
    if df.empty:
        return jsonify({"error": "No dataset available"}), 500

    if not job_title or not sector_in:
        return jsonify({"error": "Please provide job_title and sector"}), 400

    # Prepare training data & prediction
    try:
        train = df[["Avg_Salary", "Rating", "Sector"]].dropna()
        if len(train) < 20:
            base = int(df["Avg_Salary"].median() if "Avg_Salary" in df.columns else 50000)
            pred = base + rating * 2000
            confidence = 30
        else:
            le = LabelEncoder()
            train["Sector_encoded"] = le.fit_transform(train["Sector"].astype(str))
            X = train[["Rating", "Sector_encoded"]].values
            y = train["Avg_Salary"].values
            model = LinearRegression().fit(X, y)

            if sector_in in le.classes_:
                sector_encoded = int(np.where(le.classes_ == sector_in)[0][0])
                sector_match = True
            else:
                lower_classes = [c.lower() for c in le.classes_]
                if sector_in.lower() in "".join(lower_classes):
                    idx = next((i for i, c in enumerate(lower_classes) if sector_in.lower() in c), 0)
                    sector_encoded = idx
                    sector_match = True
                else:
                    sector_encoded = 0
                    sector_match = False

            pred = model.predict([[rating, sector_encoded]])[0]

            n = len(train)
            size_factor = min(1.0, n / 1000)
            residuals = y - model.predict(X)
            resid_std = np.std(residuals) if len(residuals) > 1 else np.std(y) or 1
            fit_quality = max(0.2, 1.0 - (resid_std / max(1.0, np.mean(y))))
            confidence = int(20 + 60 * size_factor * fit_quality + (15 if sector_match else 0))
            confidence = int(max(10, min(confidence, 98)))
    except Exception as e:
        print("Predict model error:", e)
        pred = int(df["Avg_Salary"].median() if "Avg_Salary" in df.columns else 50000) + rating * 1500
        confidence = 30

    pred = float(pred)
    pred = max(10000.0, min(pred, 2_000_000.0))
    min_salary = int(pred * 0.9)
    max_salary = int(pred * 1.15)

    # Recommendations
    skills_list = [s.strip().lower() for s in skills_in.replace(";", ",").split(",") if s.strip()]
    recs = []
    role_map = {
        "python": ["Data Engineer", "ML Engineer", "Data Scientist"],
        "sql": ["BI Analyst", "Data Analyst", "Database Engineer"],
        "tableau": ["BI Analyst", "Business Intelligence Developer"],
        "ml": ["Machine Learning Engineer", "Data Scientist"],
        "nlp": ["NLP Engineer", "ML Engineer"],
        "spark": ["Big Data Engineer", "Data Engineer"],
        "excel": ["Data Analyst", "Operations Analyst"],
        "aws": ["Cloud Data Engineer", "ML Engineer"]
    }
    for sk in skills_list:
        for k, roles in role_map.items():
            if k in sk and roles:
                recs.extend(roles)

    jt = job_title.lower()
    if "data scientist" in jt or "ml" in jt:
        recs = recs + ["Data Scientist", "Machine Learning Engineer"]
    if "analyst" in jt:
        recs = recs + ["Data Analyst", "BI Analyst"]
    if not recs:
        if "data" in sector_in.lower() or "analytics" in sector_in.lower():
            recs = ["Data Analyst", "Business Intelligence Analyst", "Data Scientist"]
        else:
            recs = ["Data Analyst", "Business Analyst"]

    recs = list(dict.fromkeys(recs))[:6]

    # ----- SAVE PREDICTION TO DB -----
    try:
        row = {
            "ts": datetime.utcnow().isoformat(sep=" ", timespec="seconds"),
            "job_title": job_title,
            "sector": sector_in,
            "rating": rating,
            "location": location,
            "skills": skills_in,
            "predicted_salary": int(round(pred)),
            "min_salary": int(min_salary),
            "max_salary": int(max_salary),
            "confidence": int(confidence),
            "recommendations": recs
        }
        save_prediction_row(row)
    except Exception as e:
        print("❌ Failed to save prediction:", e)

    return jsonify({
        "predicted_salary": int(round(pred)),
        "min_salary": int(min_salary),
        "max_salary": int(max_salary),
        "confidence": int(confidence),
        "recommendations": recs,
        "sector_matched": sector_in
    })

# ---------------- PREDICTION HISTORY endpoints ----------------
@app.route("/api/prediction_history")
def api_prediction_history():
    """Return recent prediction history. Query params: limit, start, end, sector, location"""
    limit = int(request.args.get("limit", 200))
    start = request.args.get("start")  # ISO timestamp or date
    end = request.args.get("end")
    sector = request.args.get("sector")
    location = request.args.get("location")

    rows = query_predictions(limit=limit, start=start, end=end, sector=sector, location=location)
    return jsonify({"count": len(rows), "predictions": rows})

@app.route("/api/prediction_export", methods=["POST"])
def api_prediction_export():
    """Export prediction history to CSV. POST body may include filters: start,end,sector,location,limit"""
    payload = request.get_json() or {}
    limit = int(payload.get("limit", 10000))
    start = payload.get("start")
    end = payload.get("end")
    sector = payload.get("sector")
    location = payload.get("location")

    rows = query_predictions(limit=limit, start=start, end=end, sector=sector, location=location)

    out = io.StringIO()
    df = pd.DataFrame(rows)
    if df.empty:
        out.write("id,ts,job_title,sector,rating,location,skills,predicted_salary,min_salary,max_salary,confidence,recommendations\n")
    else:
        # convert recommendations list back to pipe-joined string for CSV readability
        if "recommendations" in df.columns:
            df["recommendations"] = df["recommendations"].apply(lambda r: "|".join(r) if isinstance(r, list) else r)
        df.to_csv(out, index=False)
    out.seek(0)
    response = make_response(out.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=predictions_export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

# ---------------- REPORT GENERATION (kept intact) ----------------
@app.route("/api/report_generate", methods=["POST"])
def api_report_generate():
    payload = request.get_json() or {}
    year = str(payload.get("year", "")).strip()
    sector = str(payload.get("sector", "")).strip().lower()
    location = str(payload.get("location", "")).strip().lower()
    print("📩 Report Filter Received:", payload)

    df = load_df()
    if df.empty:
        return jsonify({"error": "No data"}), 404

    dff = df.copy()
    if year:
        dff = dff[dff["Year"].astype(str).str.contains(year, case=False, na=False)]
    if sector:
        dff = dff[dff["Sector"].astype(str).str.lower().str.contains(sector, na=False)]
    if location:
        dff = dff[dff["Location"].astype(str).str.lower().str.contains(location, na=False)]

    print(f"🔍 Filtered rows after filter: {len(dff)} / {len(df)}")

    if dff.empty:
        return jsonify({
            "summary": {"total_records": 0, "avg_salary": 0},
            "charts": {"salary_by_sector": [], "skills_data": [], "salary_trend": [], "top_companies": []},
            "table": []
        })

    summary = {
        "total_records": len(dff),
        "avg_salary": int(dff["Avg_Salary"].mean()),
        "top_sectors_count": dff["Sector"].value_counts().head(3).rename_axis("Sector").reset_index(name="Count").to_dict(orient="records"),
        "top_locations": dff["Location"].value_counts().head(3).rename_axis("Location").reset_index(name="Count").to_dict(orient="records")
    }

    charts = {
        "salary_by_sector": dff.groupby("Sector", as_index=False)["Avg_Salary"].mean().to_dict(orient="records"),
        "skills_data": dff["Skills"].dropna().astype(str).str.replace(";", ",").str.split(",").explode().str.strip()
                        .value_counts().head(10).rename_axis("Skill").reset_index(name="Count").to_dict(orient="records"),
        "salary_trend": dff.groupby("Year", as_index=False)["Avg_Salary"].mean().to_dict(orient="records"),
        "top_companies": dff.groupby("Company_Name", as_index=False)["Avg_Salary"].mean()
                        .sort_values("Avg_Salary", ascending=False).head(10).to_dict(orient="records")
    }

    table = dff[["Job_Title", "Company_Name", "Sector", "Location", "Rating", "Avg_Salary"]].head(200).to_dict(orient="records")

    return jsonify({"summary": summary, "charts": charts, "table": table})

# ---------------- EXPORT ----------------
@app.route("/api/report_export", methods=["POST"])
def api_report_export():
    payload = request.get_json() or {}
    year = str(payload.get("year", "")).strip()
    sector = str(payload.get("sector", "")).strip().lower()
    location = str(payload.get("location", "")).strip().lower()

    df = load_df()
    if df.empty:
        return jsonify({"error": "No data"}), 404

    dff = df.copy()
    if year:
        dff = dff[dff["Year"].astype(str).str.contains(year, case=False, na=False)]
    if sector:
        dff = dff[dff["Sector"].astype(str).str.lower().str.contains(sector, na=False)]
    if location:
        dff = dff[dff["Location"].astype(str).str.lower().str.contains(location, na=False)]

    if dff.empty:
        return jsonify({"error": "No records to export."}), 404

    out = io.StringIO()
    dff.to_csv(out, index=False)
    out.seek(0)
    response = make_response(out.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=report_export.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

if __name__ == "__main__":
    print("🚀 Launching Data Analyst Insight Portal → http://127.0.0.1:5000")
    app.run(debug=True)
