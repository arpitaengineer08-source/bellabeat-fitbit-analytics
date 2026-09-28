import os, sqlite3, pandas as pd
C = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned")
P = os.path.join(os.path.dirname(__file__), "..", "data", "fitbit_lite.db")
T = {"dailyActivity_merged.csv": "daily_activity", "sleepDay_merged.csv": "sleep_day",
     "weightLogInfo_merged.csv": "weight_log", "hourlySteps_merged.csv": "hourly_steps",
     "hourlyCalories_merged.csv": "hourly_calories", "hourlyIntensities_merged.csv": "hourly_intensities"}
if os.path.exists(P):
    os.remove(P)
con = sqlite3.connect(P)
for f, t in T.items():
    df = pd.read_csv(os.path.join(C, f))
    df.to_sql(t, con, index=False)
    print(t, len(df))
con.close()
