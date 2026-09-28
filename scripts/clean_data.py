"""
clean_data.py
-------------
Cleans the raw Fitabase/Fitbit CSV export (Bellabeat case study dataset).

What it does for every file in data/raw/:
  1. Loads the CSV.
  2. Removes exact duplicate rows.
  3. Handles missing values:
       - Most files in this dataset have 0 nulls already.
       - weightLogInfo_merged.csv: the 'Fat' column is ~97% missing
         (only 2 of 67 rows have a value), so it is dropped entirely
         instead of dropping almost every row. Every other column in
         that file is fully populated.
       - Any other numeric column with nulls (if present) is filled
         with the column median; any other text/ID column with nulls
         is dropped as a row (since an ID/date can't be guessed).
  4. Standardizes date columns to proper datetime objects.
  5. Saves the cleaned file to data/cleaned/ with the same file name.

Run:
    python scripts/clean_data.py
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned")

# Columns that are actually dates/timestamps, per file, so we can parse them properly.
# Each maps to (column_name, strptime_format) - explicit formats make parsing on
# million-row files fast instead of falling back to slow per-row inference.
DATE_ONLY = "%m/%d/%Y"
DATE_TIME = "%m/%d/%Y %I:%M:%S %p"

DATE_COLUMNS = {
    "dailyActivity_merged.csv": [("ActivityDate", DATE_ONLY)],
    "dailyCalories_merged.csv": [("ActivityDay", DATE_ONLY)],
    "dailyIntensities_merged.csv": [("ActivityDay", DATE_ONLY)],
    "dailySteps_merged.csv": [("ActivityDay", DATE_ONLY)],
    "heartrate_seconds_merged.csv": [("Time", DATE_TIME)],
    "hourlyCalories_merged.csv": [("ActivityHour", DATE_TIME)],
    "hourlyIntensities_merged.csv": [("ActivityHour", DATE_TIME)],
    "hourlySteps_merged.csv": [("ActivityHour", DATE_TIME)],
    "minuteCaloriesNarrow_merged.csv": [("ActivityMinute", DATE_TIME)],
    "minuteCaloriesWide_merged.csv": [("ActivityHour", DATE_TIME)],
    "minuteIntensitiesNarrow_merged.csv": [("ActivityMinute", DATE_TIME)],
    "minuteIntensitiesWide_merged.csv": [("ActivityHour", DATE_TIME)],
    "minuteMETsNarrow_merged.csv": [("ActivityMinute", DATE_TIME)],
    "minuteSleep_merged.csv": [("date", DATE_TIME)],
    "minuteStepsNarrow_merged.csv": [("ActivityMinute", DATE_TIME)],
    "minuteStepsWide_merged.csv": [("ActivityHour", DATE_TIME)],
    "sleepDay_merged.csv": [("SleepDay", DATE_TIME)],
    "weightLogInfo_merged.csv": [("Date", DATE_TIME)],
}


def clean_file(filename: str) -> None:
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)

    rows_before = len(df)
    nulls_before = int(df.isnull().sum().sum())
    dupes_before = int(df.duplicated().sum())

    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()

    # 2. File-specific null handling
    if filename == "weightLogInfo_merged.csv" and "Fat" in df.columns:
        df = df.drop(columns=["Fat"])

    # Generic null handling for anything left:
    #   numeric -> fill with column median
    #   non-numeric -> drop rows missing that value
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
    if non_numeric_cols:
        df = df.dropna(subset=non_numeric_cols)

    # Drop any row that is still fully/partially null just in case
    df = df.dropna()

    # 3. Parse date/time columns properly (explicit format = fast even on 1M+ rows)
    date_cols_present = []
    for col, fmt in DATE_COLUMNS.get(filename, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
            date_cols_present.append(col)
    if date_cols_present:
        df = df.dropna(subset=date_cols_present)

    # 4. Save cleaned file
    os.makedirs(CLEAN_DIR, exist_ok=True)
    out_path = os.path.join(CLEAN_DIR, filename)
    df.to_csv(out_path, index=False)

    rows_after = len(df)
    print(
        f"{filename:35s} rows {rows_before:>8d} -> {rows_after:>8d} | "
        f"nulls removed: {nulls_before:>4d} | duplicates removed: {dupes_before:>4d}"
    )


def main():
    import sys
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".csv"))
    print(f"Processing {len(files)} CSV file(s)\n")
    for f in files:
        clean_file(f)
    print(f"\nDone. Cleaned files saved to: {os.path.abspath(CLEAN_DIR)}")


if __name__ == "__main__":
    main()
