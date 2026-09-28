# Bellabeat / Fitbit Fitness Data Analytics — Case Study

A ready-to-run data analytics project built on the Fitabase Fitbit tracker
export (`4.12.16` – `5.12.16`, 30 users). Set up to open directly in VS Code.

## Project structure

```
project/
├── data/
│   ├── raw/        original CSVs, exactly as exported (untouched)
│   └── cleaned/    same 18 files after cleaning (see below)
├── scripts/
│   └── clean_data.py   cleans data/raw -> data/cleaned
├── notebooks/
│   └── analysis.ipynb  starter EDA notebook (loads the cleaned data)
├── outputs/         put charts / exported results here
├── requirements.txt
└── README.md
```

## What the cleaning step does (`scripts/clean_data.py`)

| Step | Detail |
|---|---|
| Duplicates | Exact duplicate rows dropped (found in `minuteSleep_merged.csv` — 543 rows, and `sleepDay_merged.csv` — 3 rows) |
| Nulls | `weightLogInfo_merged.csv` had a `Fat` column that was **97% empty** (65 of 67 rows) — the column is dropped rather than deleting nearly the whole file. All other files had **0 null values** in the raw export. |
| Dates | Every date/time column is parsed into a proper `datetime` type instead of being left as text, and any row where a date fails to parse is dropped. |

Re-run it any time with:

```bash
python scripts/clean_data.py
```

or clean just specific files:

```bash
python scripts/clean_data.py dailyActivity_merged.csv sleepDay_merged.csv
```

## Setup (VS Code)

1. Open this folder in VS Code (`File -> Open Folder...`).
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Select the `.venv` interpreter in VS Code (bottom-right corner, or
   `Ctrl+Shift+P` → "Python: Select Interpreter").
5. Open `notebooks/analysis.ipynb` and run the cells, or work straight from
   `data/cleaned/*.csv` in your own script.

## Data files (in `data/cleaned/`)

- `dailyActivity_merged.csv` — daily steps, distance, activity minutes, calories
- `dailyCalories_merged.csv`, `dailyIntensities_merged.csv`, `dailySteps_merged.csv` — daily breakdowns
- `hourlyCalories_merged.csv`, `hourlyIntensities_merged.csv`, `hourlySteps_merged.csv` — hourly breakdowns
- `minute*Narrow_merged.csv` / `minute*Wide_merged.csv` — minute-level calories, intensity, METs, steps (narrow = long format, wide = one column per minute)
- `minuteSleep_merged.csv`, `sleepDay_merged.csv` — sleep logs
- `heartrate_seconds_merged.csv` — second-level heart rate
- `weightLogInfo_merged.csv` — manual/auto weight log entries

## Suggested next steps

- SQL: load `data/cleaned/*.csv` into SQLite/Postgres for querying.
- Python: use `notebooks/analysis.ipynb` for EDA with pandas/matplotlib/seaborn.
- Dashboard: point Power BI / Tableau / Streamlit at `data/cleaned/`.
