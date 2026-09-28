"""
build_db.py
-----------
Loads every cleaned CSV in data/cleaned/ into a single SQLite database
(data/fitbit.db), one table per file, so the data can be queried with SQL
(and is what the Streamlit app / SQL analysis tab reads from).

Run:
    python scripts/build_db.py
"""

import os
import sqlite3
import pandas as pd

CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fitbit.db")

TABLE_MAP = {
    "dailyActivity_merged.csv": "daily_activity",
    "dailyCalories_merged.csv": "daily_calories",
    "dailyIntensities_merged.csv": "daily_intensities",
    "dailySteps_merged.csv": "daily_steps",
    "heartrate_seconds_merged.csv": "heartrate_seconds",
    "hourlyCalories_merged.csv": "hourly_calories",
    "hourlyIntensities_merged.csv": "hourly_intensities",
    "hourlySteps_merged.csv": "hourly_steps",
    "minuteCaloriesNarrow_merged.csv": "minute_calories",
    "minuteIntensitiesNarrow_merged.csv": "minute_intensities",
    "minuteMETsNarrow_merged.csv": "minute_mets",
    "minuteSleep_merged.csv": "minute_sleep",
    "minuteStepsNarrow_merged.csv": "minute_steps",
    "sleepDay_merged.csv": "sleep_day",
    "weightLogInfo_merged.csv": "weight_log",
}


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    print(f"Building database at {os.path.abspath(DB_PATH)}\n")

    for filename, table in TABLE_MAP.items():
        path = os.path.join(CLEAN_DIR, filename)
        if not os.path.exists(path):
            print(f"  [skip] {filename} not found")
            continue
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"  {filename:35s} -> table '{table}'  ({len(df)} rows)")

    conn.commit()
    conn.close()
    print("\nDone. Query it with sqlite3, pandas.read_sql, or the Streamlit app.")


if __name__ == "__main__":
    main()