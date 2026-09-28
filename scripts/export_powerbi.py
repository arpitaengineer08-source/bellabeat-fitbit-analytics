"""Exports Power BI / Tableau-ready tables to powerbi_data/ (run: python scripts/export_powerbi.py)"""
import os, pandas as pd
B = os.path.dirname(__file__); C = os.path.join(B, "..", "data", "cleaned"); O = os.path.join(B, "..", "powerbi_data")
os.makedirs(O, exist_ok=True)
d = pd.read_csv(os.path.join(C, "dailyActivity_merged.csv"), parse_dates=["ActivityDate"])
d["Weekday"] = d["ActivityDate"].dt.day_name(); d["WeekdayNo"] = d["ActivityDate"].dt.dayofweek + 1
d["ActiveMinutes"] = d[["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes"]].sum(axis=1)
d["MeetsWHO"] = ((d["FairlyActiveMinutes"] + d["VeryActiveMinutes"]) >= 150 / 7).astype(int)
d["StepClass"] = pd.cut(d["TotalSteps"], [-1, 4999, 7499, 9999, 12499, 1e9], labels=["Sedentary", "Low active", "Somewhat active", "Active", "Highly active"])
s = pd.read_csv(os.path.join(C, "sleepDay_merged.csv"), parse_dates=["SleepDay"]); s["Efficiency"] = s["TotalMinutesAsleep"] / s["TotalTimeInBed"] * 100
h = pd.read_csv(os.path.join(C, "hourlySteps_merged.csv")).merge(pd.read_csv(os.path.join(C, "hourlyCalories_merged.csv")), on=["Id", "ActivityHour"])
h["Hour"] = pd.to_datetime(h["ActivityHour"]).dt.hour
u = d.groupby("Id").agg(AvgSteps=("TotalSteps", "mean"), AvgCalories=("Calories", "mean"), AvgSedentaryMin=("SedentaryMinutes", "mean"), Days=("Id", "size")).reset_index()
for n, x in {"daily_activity": d, "sleep_day": s, "hourly": h, "user_summary": u}.items():
    x.to_csv(os.path.join(O, n + ".csv"), index=False); print(n, len(x))