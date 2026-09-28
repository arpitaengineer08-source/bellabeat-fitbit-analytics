"""
quick_eda.py
------------
Fast, no-notebook EDA on the cleaned Fitbit data. Run straight from the
terminal (much faster than a Jupyter kernel):

    python scripts/quick_eda.py

Produces PNG charts in outputs/ and prints key numbers to the terminal.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_style("whitegrid")


def load_data():
    daily = pd.read_csv(os.path.join(CLEAN_DIR, "dailyActivity_merged.csv"), parse_dates=["ActivityDate"])
    sleep = pd.read_csv(os.path.join(CLEAN_DIR, "sleepDay_merged.csv"), parse_dates=["SleepDay"])
    weight = pd.read_csv(os.path.join(CLEAN_DIR, "weightLogInfo_merged.csv"), parse_dates=["Date"])
    return daily, sleep, weight


def basic_summary(daily, sleep, weight):
    print("=" * 60)
    print("BASIC SUMMARY")
    print("=" * 60)
    print(f"daily activity : {daily.shape}  |  unique users: {daily['Id'].nunique()}")
    print(f"sleep          : {sleep.shape}  |  unique users: {sleep['Id'].nunique()}")
    print(f"weight         : {weight.shape}  |  unique users: {weight['Id'].nunique()}")
    print()
    print("Averages across all users/days:")
    print(f"  Avg daily steps    : {daily['TotalSteps'].mean():,.0f}")
    print(f"  Avg calories burned: {daily['Calories'].mean():,.0f}")
    print(f"  Avg sleep (minutes): {sleep['TotalMinutesAsleep'].mean():,.0f}  (~{sleep['TotalMinutesAsleep'].mean()/60:.1f} hrs)")
    print()


def chart_steps_vs_calories(daily):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=daily, x="TotalSteps", y="Calories", ax=ax, alpha=0.6)
    ax.set_title("Total Steps vs. Calories Burned")
    path = os.path.join(OUT_DIR, "steps_vs_calories.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def chart_activity_breakdown(daily):
    activity_cols = ["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]
    avg_minutes = daily[activity_cols].mean()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(avg_minutes, labels=avg_minutes.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Average Daily Minutes by Activity Level")
    path = os.path.join(OUT_DIR, "activity_breakdown.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")
    print("Activity minute averages per day:")
    print(avg_minutes.round(1).to_string())
    print()


def chart_sleep_vs_steps(daily, sleep):
    merged = pd.merge(
        daily, sleep,
        left_on=["Id", "ActivityDate"], right_on=["Id", "SleepDay"],
        how="inner",
    )
    print(f"Matched daily-activity + sleep records: {merged.shape[0]} rows")

    corr = merged[["TotalSteps", "TotalMinutesAsleep", "TotalTimeInBed", "Calories"]].corr()
    print("\nCorrelation matrix (steps / sleep / time in bed / calories):")
    print(corr.round(2).to_string())

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=merged, x="TotalSteps", y="TotalMinutesAsleep", ax=ax, alpha=0.6)
    ax.set_title("Steps vs. Minutes Asleep")
    path = os.path.join(OUT_DIR, "steps_vs_sleep.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}\n")
    return merged


def chart_weight_trend(weight):
    if weight.empty:
        print("No weight data to chart.")
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    for uid, grp in weight.groupby("Id"):
        grp = grp.sort_values("Date")
        ax.plot(grp["Date"], grp["WeightKg"], marker="o", label=str(uid))
    ax.set_title("Weight (kg) Over Time, by User")
    ax.set_ylabel("Weight (kg)")
    ax.legend(title="User ID", fontsize=8)
    path = os.path.join(OUT_DIR, "weight_trend.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    daily, sleep, weight = load_data()
    basic_summary(daily, sleep, weight)
    chart_steps_vs_calories(daily)
    chart_activity_breakdown(daily)
    chart_sleep_vs_steps(daily, sleep)
    chart_weight_trend(weight)
    print("\nAll done. Check the outputs/ folder for charts.")


if __name__ == "__main__":
    main()