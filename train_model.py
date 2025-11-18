# train_model.py
import os, json
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# -------------------------------
# 1. Ensure model folder exists
# -------------------------------
os.makedirs("model", exist_ok=True)

# -------------------------------
# 2. Load and clean dataset
# -------------------------------
df = pd.read_csv("data/data_analyst_jobs.csv", encoding="utf-8")

# Handle missing / incorrect data types
df['Avg_Salary'] = pd.to_numeric(df['Avg_Salary'], errors='coerce').fillna(0)
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(df['Rating'].median())
df['Size'] = df['Size'].fillna("Unknown")
df['Company_Name'] = df['Company_Name'].fillna("Unknown")
df['Sector'] = df['Sector'].fillna("Unknown")
df['Skills'] = df['Skills'].fillna("")

# Create a new feature: Skill Count
df['Skill_Count'] = df['Skills'].apply(lambda s: len(str(s).split(';')) if s else 0)

# -------------------------------
# 3. Define features and target
# -------------------------------
X = df[['Rating', 'Size', 'Company_Name', 'Sector', 'Skill_Count']]
y = df['Avg_Salary']

# -------------------------------
# 4. Encode categorical features
# -------------------------------
cols_cat = ['Size', 'Company_Name', 'Sector']

transformer = ColumnTransformer(
    transformers=[
        ('ohe', OneHotEncoder(handle_unknown='ignore'), cols_cat)
    ],
    remainder='passthrough'  # keep numeric columns (Rating, Skill_Count)
)

# -------------------------------
# 5. Build pipeline (preprocess + model)
# -------------------------------
pipeline = Pipeline([
    ('transform', transformer),
    ('rf', RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        n_jobs=-1,
        max_depth=12,
        min_samples_split=4
    ))
])

# -------------------------------
# 6. Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# -------------------------------
# 7. Train the model
# -------------------------------
print("🚀 Training model, please wait...")
pipeline.fit(X_train, y_train)
print("✅ Model training completed successfully.")

# -------------------------------
# 8. Save model and metadata
# -------------------------------
joblib.dump(pipeline, "model/salary_model.pkl")

# Extract one-hot feature names (optional)
try:
    ohe = pipeline.named_steps['transform'].named_transformers_['ohe']
    feature_names = list(ohe.get_feature_names_out(cols_cat)) + ['Rating', 'Skill_Count']
except Exception as e:
    print("⚠️ Could not extract feature names:", e)
    feature_names = ['Rating', 'Skill_Count']

with open("model/feature_columns.json", "w") as f:
    json.dump(feature_names, f)

print("💾 Model saved as → model/salary_model.pkl")
print("📋 Feature columns saved → model/feature_columns.json")

# -------------------------------
# 9. Optional: Evaluate accuracy
# -------------------------------
r2 = pipeline.score(X_test, y_test)
print(f"📊 Model R² Score: {r2:.3f}")
