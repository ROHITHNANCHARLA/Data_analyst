# generate_sample_data.py
import csv, os, random
from faker import Faker
from datetime import datetime
fake = Faker()

OUT = os.path.join("data","data_analyst_jobs.csv")
os.makedirs("data", exist_ok=True)

companies = ["DataWorks","AnalyticaX","Insightify","TechPulse","FinSight","BioStats","RetailEdge","HealthSense"]
locations = ["New York, NY","San Francisco, CA","Bengaluru, KA","Mumbai, MH","Delhi, DL","Hyderabad, TS","Pune, MH","Chennai, TN"]
industries = ["Information Technology","Finance","Healthcare","Retail","Biotech","E-Commerce","Education","Consulting"]
ownerships = ["Private", "Public", "Subsidiary", "Non-profit"]
sectors = ["Analytics","Data Science","Business Intelligence","Research","Product"]
skills_pool = ["Python","SQL","Excel","Tableau","PowerBI","R","Spark","AWS","NLP","Deep Learning","Statistics","Git"]

def random_skills():
    return ";".join(random.sample(skills_pool, k=random.randint(2,6)))

rows = []
for i in range(2500):
    title = random.choice(["Data Analyst","Senior Data Analyst","Data Scientist","BI Analyst","Research Analyst"])
    salary_low = random.randint(30,100) * 1000
    salary_high = salary_low + random.randint(5,60) * 1000
    rating = random.choice(["", round(random.uniform(2.5, 4.8), 1)])  # ✅ fixed line
    company = random.choice(companies)
    location = random.choice(locations)
    hq = random.choice(locations)
    size = random.choice(["1-50","51-200","201-1000","1001-5000","5000+"])
    industry = random.choice(industries)
    sector = random.choice(sectors)
    revenue = random.choice(["<1M","1M-10M","10M-100M","100M-1B",">1B"])
    easy_apply = random.choice(["Yes","No"])
    year = random.randint(2016,2025)
    month = random.randint(1,12)
    date = f"{year}-{month:02d}-{random.randint(1,28):02d}"
    desc = fake.paragraph(nb_sentences=3)
    skills = random_skills()
    min_sal = salary_low
    max_sal = salary_high
    avg_sal = int((min_sal + max_sal)/2)
    rows.append([
        title, f"${min_sal//1000}K-${max_sal//1000}K", rating or "", company, location,
        hq, size, ownerships, industry, sector, revenue, easy_apply, desc, skills,
        min_sal, max_sal, avg_sal, date
    ])

header = ["Job_Title","Salary_Estimate","Rating","Company_Name","Location","Headquarters","Size","Type_of_Ownership","Industry","Sector","Revenue","Easy_Apply","Job_Description","Skills","Min_Salary","Max_Salary","Avg_Salary","Date"]
with open(OUT, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Generated {len(rows)} rows -> {OUT}")
