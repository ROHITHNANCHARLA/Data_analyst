📊 Data Analyst Jobs Insight Portal

Author: ROHITH NANCHARLA
Theme: Dark Cyber Theme
Tech Stack: Flask, Python, SQLite, HTML/CSS, JS, Bootstrap, Plotly

📝 Project Summary

The Data Analyst Jobs Insight Portal is a full-stack analytics platform designed to analyze job market trends, visualize salary insights, and provide AI-assisted salary predictions for Data Analyst roles.
It integrates interactive dashboards, deep analytics, smart autocomplete, ML-based salary prediction, and exportable reports, all wrapped in a modern Dark Cyber UI.

This system mimics a real-world HR analytics tool and is built for academic, professional, and portfolio use.

🚀 Key Features
📌 1. Interactive Dashboard

KPIs (Total Records, Average Salary, Top Sector, Top Location)

Salary Trends by Year

Top States & Companies

Skill Radar Chart

Fully responsive Plotly graphs matching Dark Cyber theme

📌 2. Advanced Analytics Module

Multi-filter analysis (Year, Sector, Location)

Fuzzy matching for misspellings

Smart Autocomplete (AI-like field assist)

Skill demand charts

Sector-wise and rating-wise salary insights

AI-generated summary of matched data

📌 3. Salary Predictor (AI-Assisted)

Linear Regression using rating + encoded sector

Smart sector handling (fallback for new/unknown sectors)

Min-Max salary range

Confidence score (%)

Recommended job roles based on skills

Animated gauges and prediction UI

📌 4. Report Center (SQLite History + CSV Export)

Every prediction auto-saved in local SQLite DB

View all historical predictions

Clean and animated report table UI

Download full prediction history as .csv

📌 5. Clean, Modern UI (Dark Cyber Theme)

Neon blue glow

Floating particles / glassmorphism cards

Smooth animations

Sleek Bootstrap components

📂 File Structure (Recommended)
project/
│── app.py
│── requirements.txt
│── /data
│     └── data_analyst_jobs.csv
│     └── predictions.db
│── /templates
│     ├── layout.html
│     ├── dashboard.html
│     ├── analytics.html
│     ├── predictor.html
│     └── reports.html
│── /static
      ├── /css
      │     └── style.css
      └── /js
            ├── main.js
            ├── dashboard.js
            ├── autocomplete.js
            └── reports.js

📦 Dataset

Your dataset should contain:

Job_Title
Company_Name
Sector
Location
Date
Avg_Salary
Min_Salary
Max_Salary
Rating
Skills


If Year is missing, it is extracted automatically from the Date column.

⚙️ Installation & Setup
1️⃣ Create virtual environment
python -m venv venv

2️⃣ Activate environment

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
python app.py

5️⃣ Open in browser
http://127.0.0.1:5000

🧠 Machine Learning Model (Short Overview)

Model: Linear Regression

Inputs: Rating, Encoded Sector

Output: Predicted Salary

Sector Encoding: LabelEncoder with nearest-match fallback

Confidence Score: Based on training size & model fit

Recommendations: Keyword-based mapping to job roles

📤 API Endpoints
🔹 Analytics Filter

POST /api/analytics_filter

🔹 Salary Prediction

POST /api/predict_salary

🔹 Prediction History

GET /api/prediction_history

🔹 Export CSV

POST /api/prediction_export

🌟 What Makes This Project Special?

✔ Highly visual + animated UI
✔ Real backend + ML model
✔ Smart fuzzy search + autocomplete
✔ SQLite-backed history
✔ Production-style project structure
✔ Looks premium in demos/portfolio

📘 Summary

Built a Data Analyst Job Insight Portal using Flask, Plotly and SQLite with an interactive dashboard and real-time analytics.

Implemented an ML-powered salary predictor using sector encoding, confidence scoring, and AI role recommendations.

Added downloadable CSV reports, analytics filtering, and smart autocomplete for robust UX.

Designed a modern Dark Cyber Theme UI featuring animated Plotly charts and smooth page transitions.
