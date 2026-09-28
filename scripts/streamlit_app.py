"""
Bellabeat x Fitbit: Consumer Wellness Analytics
Run:  streamlit run scripts/streamlit_app.py
"""
import os
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE = os.path.dirname(__file__)
CLEAN_DIR = os.path.join(BASE, "..", "data", "cleaned")
DB_PATH = os.path.join(BASE, "..", "data", "fitbit.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(BASE, "..", "data", "fitbit_lite.db")

st.set_page_config(page_title="Bellabeat Wellness Analytics", layout="wide", page_icon="🌿")

TEAL, INDIGO, AMBER, ROSE, SLATE = "#2DD4BF", "#818CF8", "#FBBF24", "#FB7185", "#64748B"
SEQ = [TEAL, INDIGO, AMBER, ROSE, "#38BDF8", SLATE]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: #0B1220; color: #E2E8F0; }}
[data-testid="stSidebar"] {{ background: #0F192B; border-right: 1px solid #1E2A44; }}
.block-container {{ padding-top: 2rem; max-width: 1250px; }}
h1, h2, h3 {{ letter-spacing: -0.02em; color: #F1F5F9; }}
.hero {{ padding: 26px 30px; border-radius: 16px; margin-bottom: 18px;
  background: linear-gradient(120deg, #10233F 0%, #0F3A45 60%, #114B4A 100%); border: 1px solid #1E3A5F; }}
.hero .eyebrow {{ color: {TEAL}; font-size: .75rem; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }}
.hero h1 {{ margin: 6px 0 6px; font-size: 2rem; }}
.hero p {{ color: #A9B8CF; margin: 0; font-size: .95rem; max-width: 820px; }}
.kpi {{ background: #111C31; border: 1px solid #1E2A44; border-radius: 12px; padding: 16px 18px; height: 100%; }}
.kpi .l {{ color: #8FA1BD; font-size: .72rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }}
.kpi .v {{ color: #F8FAFC; font-size: 1.75rem; font-weight: 700; margin: 4px 0 2px; }}
.kpi .s {{ color: #6F819E; font-size: .76rem; }}
.finding {{ background: #111C31; border: 1px solid #1E2A44; border-left: 4px solid {TEAL};
  border-radius: 10px; padding: 16px 18px; height: 100%; }}
.finding .n {{ color: {TEAL}; font-weight: 700; font-size: 1.5rem; }}
.finding .t {{ color: #F1F5F9; font-weight: 600; margin: 2px 0 6px; }}
.finding .d {{ color: #9DB0CB; font-size: .85rem; line-height: 1.45; }}
.sowhat {{ background: rgba(45,212,191,.08); border: 1px solid rgba(45,212,191,.25); border-radius: 10px;
  padding: 12px 16px; color: #CFE9E5; font-size: .88rem; margin-top: 8px; }}
.sowhat b {{ color: {TEAL}; }}
.cap {{ color: #7A8CA8; font-size: .78rem; margin-top: -6px; }}
button[data-baseweb="tab"] {{ font-weight: 600; }}
</style>""", unsafe_allow_html=True)


def kpi(label, value, sub=""):
    st.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def finding(num, title, desc, color=TEAL):
    st.markdown(f'<div class="finding" style="border-left-color:{color}"><div class="n" style="color:{color}">{num}</div>'
                f'<div class="t">{title}</div><div class="d">{desc}</div></div>', unsafe_allow_html=True)


def sowhat(text):
    st.markdown(f'<div class="sowhat"><b>So what?</b> {text}</div>', unsafe_allow_html=True)


def style(fig, h=360):
    fig.update_layout(
        height=h, margin=dict(l=8, r=8, t=28, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#B8C4D9", size=12), legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(gridcolor="#1B2740", zeroline=False), yaxis=dict(gridcolor="#1B2740", zeroline=False),
    )
    return fig


@st.cache_data
def load():
    d = pd.read_csv(os.path.join(CLEAN_DIR, "dailyActivity_merged.csv"), parse_dates=["ActivityDate"])
    s = pd.read_csv(os.path.join(CLEAN_DIR, "sleepDay_merged.csv"), parse_dates=["SleepDay"])
    w = pd.read_csv(os.path.join(CLEAN_DIR, "weightLogInfo_merged.csv"), parse_dates=["Date"])
    h = pd.read_csv(os.path.join(CLEAN_DIR, "hourlySteps_merged.csv"), parse_dates=["ActivityHour"])
    d["Weekday"] = d["ActivityDate"].dt.day_name()
    d["ModVig"] = d["FairlyActiveMinutes"] + d["VeryActiveMinutes"]
    d["Class"] = pd.cut(d["TotalSteps"], [-1, 4999, 7499, 9999, 12499, 1e9],
                        labels=["Sedentary (<5k)", "Low active (5–7.5k)", "Somewhat active (7.5–10k)",
                                "Active (10–12.5k)", "Highly active (12.5k+)"])
    s["Efficiency"] = s["TotalMinutesAsleep"] / s["TotalTimeInBed"] * 100
    h["Hour"] = h["ActivityHour"].dt.hour
    d["NonWear"] = (d["SedentaryMinutes"] >= 1440) | (d["TotalSteps"] == 0)
    hc = pd.read_csv(os.path.join(CLEAN_DIR, "hourlyCalories_merged.csv"), parse_dates=["ActivityHour"])
    hc["Hour"] = hc["ActivityHour"].dt.hour
    return d, s, w, h, hc


def sql(q):
    con = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(q, con)
    finally:
        con.close()


D, S, W, H, HC = load()
N = D["Id"].nunique()

st.sidebar.markdown("### 🌿 Bellabeat Analytics")
st.sidebar.caption("Fitabase Fitbit export · 12 Apr – 12 May 2016 · 33 consented users")
users = st.sidebar.multiselect("Cohort filter (user ID)", sorted(D["Id"].unique()), help="Empty = all users")
wear = st.sidebar.checkbox("Exclude non-wear days", value=True, help="Drops days with 1,440 sedentary min or 0 steps (tracker not worn)")
D = D[~D["NonWear"]] if wear else D
d = D[D["Id"].isin(users)] if users else D
s = S[S["Id"].isin(users)] if users else S
w = W[W["Id"].isin(users)] if users else W
if d.empty:
    st.stop()
st.sidebar.divider()
st.sidebar.markdown("**Benchmarks used**\n- Steps: Tudor-Locke & Bassett classification\n- Activity: WHO 150 min/wk moderate-to-vigorous (≈21 min/day)\n- Sleep: 7–9 h adults; efficiency ≥85% considered healthy")
st.sidebar.divider()
st.sidebar.markdown("**Data preparation**\n- `Fat` dropped (97% null)\n- 546 duplicate sleep rows removed\n- Dates parsed to datetime")

# ------------------------------------------------------------ derived metrics
who_pct = (d["ModVig"] >= 150 / 7).mean() * 100
sed_h = d["SedentaryMinutes"].mean() / 60
active_min = d["ModVig"].mean()
pct_10k = (d["TotalSteps"] >= 10000).mean() * 100
sleep_h = s["TotalMinutesAsleep"].mean() / 60 if len(s) else float("nan")
eff = s["Efficiency"].mean() if len(s) else float("nan")
hr = H.groupby("Hour")["StepTotal"].mean()
peak_hr = int(hr.idxmax())
wk_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wk = d.groupby("Weekday")["TotalSteps"].mean().reindex(wk_order)

st.markdown(f"""<div class="hero"><div class="eyebrow">Consumer wellness · Smart-device usage analysis</div>
<h1>How do people really use their fitness trackers?</h1>
<p>Business question: which usage patterns in Fitbit data reveal growth opportunities for Bellabeat's
Leaf, Time, Spring and app ecosystem, with a focus on women's health and everyday wellness.</p></div>""", unsafe_allow_html=True)

t0, t1, t2, t3, t4, t5, t7, t6 = st.tabs(["Case study", "Executive summary", "Activity", "Sleep", "Users & engagement", "Recommendations", "Deep dive", "SQL lab"])

# =========================================================== EXECUTIVE SUMMARY
with t1:
    c = st.columns(5)
    with c[0]: kpi("Users", f"{d['Id'].nunique()}", f"{len(d):,} user-days")
    with c[1]: kpi("Avg steps / day", f"{d['TotalSteps'].mean():,.0f}", f"{pct_10k:.0f}% of days ≥ 10k")
    with c[2]: kpi("Meets WHO activity", f"{who_pct:.0f}%", "of days ≥ 21 min MVPA")
    with c[3]: kpi("Avg sleep", f"{sleep_h:.1f} h", f"efficiency {eff:.0f}%")
    with c[4]: kpi("Sedentary time", f"{sed_h:.1f} h", "per day (device-worn)")
    st.write("")
    f = st.columns(3)
    with f[0]:
        finding(f"{sed_h:.0f} h", "Sedentary time dominates the day",
                f"Users average only {active_min:.0f} min/day of moderate-to-vigorous activity against {sed_h:.1f} h sedentary.", ROSE)
    with f[1]:
        finding(f"{who_pct:.0f}%", "Days meeting WHO activity guidance",
                "Share of user-days reaching ≈21 min/day of moderate-to-vigorous activity (150 min/week).", AMBER)
    with f[2]:
        finding(f"{S['Id'].nunique()}/{N}", "Sleep tracking is under-used",
                f"Only {W['Id'].nunique()} of {N} users logged weight. Passive tracking wins; manual logging drops off.", INDIGO)
    st.write("")
    a, b = st.columns([3, 2])
    with a:
        st.subheader("Steps-based activity profile")
        cl = d["Class"].value_counts(normalize=True).sort_index().mul(100).reset_index()
        cl.columns = ["Class", "Share"]
        fig = px.bar(cl, x="Share", y="Class", orientation="h", text=cl["Share"].round(0).astype(int).astype(str) + "%",
                     color="Class", color_discrete_sequence=[ROSE, AMBER, "#38BDF8", TEAL, INDIGO])
        fig.update_layout(showlegend=False, xaxis_title="% of user-days", yaxis_title="")
        st.plotly_chart(style(fig, 330), use_container_width=True)
    with b:
        st.subheader("Where the day goes")
        m = d[["SedentaryMinutes", "LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]].mean()
        fig = go.Figure(go.Pie(labels=["Sedentary", "Light", "Fairly active", "Very active"], values=m.values,
                               hole=.62, marker=dict(colors=[SLATE, "#38BDF8", AMBER, TEAL]), textinfo="percent",
                               sort=False))
        st.plotly_chart(style(fig, 330), use_container_width=True)
    sowhat("Most users are light movers rather than non-users. The opportunity is nudging light activity toward "
           "moderate intensity, not convincing people to start tracking.")

# =========================================================== ACTIVITY
with t2:
    a, b = st.columns(2)
    with a:
        st.subheader("Average steps by hour of day")
        hd = hr.reset_index()
        hd["c"] = np.where(hd["Hour"] == peak_hr, TEAL, "#2B3B5C")
        fig = go.Figure(go.Bar(x=hd["Hour"], y=hd["StepTotal"], marker_color=hd["c"]))
        fig.update_layout(xaxis_title="Hour (24h)", yaxis_title="Avg steps", xaxis=dict(dtick=2))
        st.plotly_chart(style(fig, 320), use_container_width=True)
        st.markdown(f'<div class="cap">Peak movement window: {peak_hr}:00 – {peak_hr + 1}:00</div>', unsafe_allow_html=True)
    with b:
        st.subheader("Average steps by weekday")
        fig = go.Figure(go.Bar(x=wk.index, y=wk.values,
                               marker_color=[TEAL if v == wk.max() else "#2B3B5C" for v in wk.values]))
        fig.add_hline(y=10000, line_dash="dot", line_color=AMBER, annotation_text="10k reference")
        fig.update_layout(yaxis_title="Avg steps")
        st.plotly_chart(style(fig, 320), use_container_width=True)
        st.markdown(f'<div class="cap">Most active: {wk.idxmax()} ({wk.max():,.0f}) · Least active: {wk.idxmin()} ({wk.min():,.0f})</div>', unsafe_allow_html=True)
    st.subheader("Steps vs. calories burned")
    x, y = d["TotalSteps"].values, d["Calories"].values
    k, b0 = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    fig = px.scatter(d, x="TotalSteps", y="Calories", opacity=.55, color_discrete_sequence=[TEAL])
    xs = np.linspace(x.min(), x.max(), 50)
    fig.add_trace(go.Scatter(x=xs, y=k * xs + b0, mode="lines", line=dict(color=AMBER, dash="dash"), name="Linear fit"))
    st.plotly_chart(style(fig, 360), use_container_width=True)
    sowhat(f"Correlation r = {r:.2f}: every additional 1,000 steps ≈ {k * 1000:.0f} kcal. Calorie-burn framing "
           "can make step goals feel tangible inside the app.")

# =========================================================== SLEEP
with t3:
    mg = pd.merge(d, s, left_on=["Id", "ActivityDate"], right_on=["Id", "SleepDay"])
    c = st.columns(4)
    with c[0]: kpi("Nights logged", f"{len(s)}", f"{s['Id'].nunique()} users")
    with c[1]: kpi("Avg sleep", f"{sleep_h:.1f} h", "target 7–9 h")
    with c[2]: kpi("Sleep efficiency", f"{eff:.0f}%", "asleep ÷ in bed")
    with c[3]: kpi("Nights < 7 h", f"{(s['TotalMinutesAsleep'] < 420).mean() * 100:.0f}%", "short-sleep nights")
    st.write("")
    a, b = st.columns(2)
    with a:
        st.subheader("Sleep duration distribution")
        fig = px.histogram(s, x=s["TotalMinutesAsleep"] / 60, nbins=28, color_discrete_sequence=[INDIGO])
        fig.add_vrect(x0=7, x1=9, fillcolor=TEAL, opacity=.12, line_width=0, annotation_text="recommended 7–9 h")
        fig.update_layout(xaxis_title="Hours asleep", yaxis_title="Nights")
        st.plotly_chart(style(fig, 330), use_container_width=True)
    with b:
        st.subheader("Sleep efficiency")
        fig = px.histogram(s[s["Efficiency"] > 60], x="Efficiency", nbins=25, color_discrete_sequence=[ROSE])
        fig.add_vline(x=85, line_dash="dash", line_color=TEAL, annotation_text="85% healthy threshold")
        fig.update_layout(xaxis_title="Efficiency (%)", yaxis_title="Nights")
        st.plotly_chart(style(fig, 330), use_container_width=True)
    if len(mg) > 2:
        r2 = mg["TotalSteps"].corr(mg["TotalMinutesAsleep"])
        st.subheader("Does more activity mean better sleep?")
        mg["Steps band"] = pd.cut(mg["TotalSteps"], [-1, 5000, 10000, 15000, 1e9], labels=["<5k", "5–10k", "10–15k", "15k+"])
        bd = mg.groupby("Steps band", observed=True)["TotalMinutesAsleep"].mean().div(60).reset_index()
        fig = px.bar(bd, x="Steps band", y="TotalMinutesAsleep", color_discrete_sequence=[INDIGO], text=bd["TotalMinutesAsleep"].round(1))
        fig.update_layout(yaxis_title="Avg hours asleep", yaxis_range=[0, 9])
        st.plotly_chart(style(fig, 300), use_container_width=True)
        sowhat(f"Steps and sleep duration correlate at r = {r2:.2f} in this sample: no evidence that more steps "
               "improve sleep here. Small sample; treat as directional, not causal.")

# =========================================================== USERS
with t4:
    a, b = st.columns([3, 2])
    with a:
        st.subheader("User leaderboard: average daily steps")
        pu = d.groupby("Id").agg(steps=("TotalSteps", "mean"), days=("ActivityDate", "count")).reset_index()
        pu["Id"] = pu["Id"].astype(str)
        pu = pu.sort_values("steps")
        fig = go.Figure(go.Bar(x=pu["steps"], y=pu["Id"], orientation="h",
                               marker_color=[TEAL if v >= 10000 else INDIGO if v >= 7500 else SLATE for v in pu["steps"]]))
        fig.update_layout(xaxis_title="Avg steps/day", yaxis=dict(type="category"))
        st.plotly_chart(style(fig, max(340, 20 * len(pu))), use_container_width=True)
    with b:
        st.subheader("Feature adoption")
        ad = pd.DataFrame({"Feature": ["Activity", "Sleep", "Weight"],
                           "Users": [N, S["Id"].nunique(), W["Id"].nunique()]})
        ad["Pct"] = ad["Users"] / N * 100
        fig = px.bar(ad, x="Feature", y="Pct", text=ad["Users"].astype(str) + " users", color="Feature",
                     color_discrete_sequence=[TEAL, INDIGO, AMBER])
        fig.update_layout(showlegend=False, yaxis_title="% of users", yaxis_range=[0, 115])
        st.plotly_chart(style(fig, 340), use_container_width=True)
    st.subheader("Weight trajectories (users who logged weight)")
    if w.empty:
        st.info("No weight logs for this cohort.")
    else:
        fig = go.Figure()
        for i, (u, g) in enumerate(w.groupby("Id")):
            g = g.sort_values("Date")
            fig.add_trace(go.Scatter(x=g["Date"], y=g["WeightKg"], mode="lines+markers", name=str(u),
                                     line=dict(color=SEQ[i % len(SEQ)])))
        fig.update_layout(yaxis_title="kg")
        st.plotly_chart(style(fig, 320), use_container_width=True)
    sowhat("Engagement drops as logging requires more effort. Automatic sleep detection and smart-scale sync "
           "would lift sleep and weight coverage without asking users to do more.")

# =========================================================== RECOMMENDATIONS
with t5:
    st.subheader("Recommendations for Bellabeat")
    recs = [
        ("1", "Turn sedentary time into a Leaf/Time nudge", TEAL,
         f"Users sit {sed_h:.1f} h/day. Send gentle move reminders, timed around the {peak_hr}:00 activity peak and low-activity windows."),
        ("2", "Coach light → moderate intensity", AMBER,
         f"Only {who_pct:.0f}% of days reach the WHO activity target. Add weekly 'active minutes' goals rather than step-only goals."),
        ("3", "Make sleep tracking automatic", INDIGO,
         f"Sleep is logged by {S['Id'].nunique()}/{N} users. Passive sleep detection and a bedtime-consistency score can raise adoption."),
        ("4", "Weekend re-engagement campaign", ROSE,
         f"{wk.idxmin()} is the lowest-step day ({wk.min():,.0f} avg). Challenges and Spring hydration prompts can lift it."),
    ]
    for i in range(0, 4, 2):
        cols = st.columns(2)
        for col, (n, t, colr, dsc) in zip(cols, recs[i:i + 2]):
            with col:
                finding(n, t, dsc, colr)
        st.write("")
    st.caption("Limitations: 33 users, 30 days, no demographics or gender data; sleep and weight samples are small. "
               "Findings are directional and should be validated on a larger cohort.")

# =========================================================== SQL
PRESETS = {
    "Integrity: full-day sedentary (tracker not worn)": "SELECT Id, COUNT(*) AS non_wear_days\nFROM daily_activity WHERE SedentaryMinutes >= 1440 GROUP BY Id ORDER BY non_wear_days DESC;",
    "Integrity: blanks, negatives, duplicates": "SELECT COUNT(*) AS rows_total,\n  SUM(TotalSteps IS NULL OR Calories IS NULL) AS null_rows,\n  SUM(TotalSteps < 0 OR Calories < 0) AS negative_rows,\n  COUNT(*) - COUNT(DISTINCT Id || ActivityDate) AS duplicate_rows\nFROM daily_activity;",
    "Calories burnt by hour of day": "SELECT strftime('%H', ActivityHour) AS hour, ROUND(AVG(Calories),1) AS avg_calories\nFROM hourly_calories GROUP BY hour ORDER BY hour;",
    "Steps by weekday (SQL)": "SELECT CASE strftime('%w', ActivityDate) WHEN '0' THEN 'Sun' WHEN '1' THEN 'Mon' WHEN '2' THEN 'Tue' WHEN '3' THEN 'Wed' WHEN '4' THEN 'Thu' WHEN '5' THEN 'Fri' ELSE 'Sat' END AS weekday,\n  ROUND(AVG(TotalSteps),0) AS avg_steps\nFROM daily_activity WHERE SedentaryMinutes < 1440 GROUP BY weekday ORDER BY avg_steps DESC;",
    "Average steps & calories per user": "SELECT Id, ROUND(AVG(TotalSteps),0) AS avg_steps, ROUND(AVG(Calories),0) AS avg_calories\nFROM daily_activity GROUP BY Id ORDER BY avg_steps DESC;",
    "Days meeting WHO activity target (per user)": "SELECT Id, COUNT(*) AS days,\n  SUM(CASE WHEN FairlyActiveMinutes+VeryActiveMinutes >= 21.4 THEN 1 ELSE 0 END) AS days_meeting_target\nFROM daily_activity GROUP BY Id ORDER BY days_meeting_target DESC;",
    "Average sleep hours & efficiency per user": "SELECT Id, ROUND(AVG(TotalMinutesAsleep)/60.0,1) AS avg_hours,\n  ROUND(AVG(TotalMinutesAsleep*100.0/TotalTimeInBed),1) AS efficiency_pct\nFROM sleep_day GROUP BY Id ORDER BY avg_hours DESC;",
    "Busiest hours (avg steps)": "SELECT strftime('%H', ActivityHour) AS hour, ROUND(AVG(StepTotal),0) AS avg_steps\nFROM hourly_steps GROUP BY hour ORDER BY avg_steps DESC LIMIT 5;",
    "Users who logged weight": "SELECT Id, COUNT(*) AS entries, ROUND(AVG(WeightKg),1) AS avg_kg, ROUND(AVG(BMI),1) AS avg_bmi\nFROM weight_log GROUP BY Id ORDER BY entries DESC;",
}
with t6:
    st.subheader("SQL lab")
    st.caption("Read-only queries on data/fitbit.db · tables: daily_activity, sleep_day, weight_log, hourly_steps, hourly_calories, hourly_intensities, minute_* , heartrate_seconds")
    if not os.path.exists(DB_PATH):
        st.error("Run `python scripts/build_db.py` first.")
    else:
        pick = st.selectbox("Preset query", list(PRESETS))
        q = st.text_area("Query", PRESETS[pick], height=130, key=pick)
        if st.button("Run query", type="primary"):
            if not q.strip().lower().startswith(("select", "with")):
                st.error("Only SELECT queries are allowed.")
            else:
                try:
                    st.dataframe(sql(q), use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")


# =========================================================== CASE STUDY
with t0:
    st.subheader("1 · Business task")
    st.markdown("**How are consumers using their smart devices, and what should Bellabeat's marketing do about it?**  \n"
                "Stakeholders: **Urška Sršen** (co-founder, CCO), **Sando Mur** (co-founder), Bellabeat marketing analytics team.  \n"
                "**Product in focus: Bellabeat Leaf**, a wearable wellness tracker (bracelet/clip). It tracks the same activity, sleep and stress signals as the Fitbit data analysed here.")
    st.subheader("2 · Data sources")
    st.markdown("Fitbit Fitness Tracker Data (Amazon Mechanical Turk survey, 12 Apr – 12 May 2016, CC0, Zenodo 10.5281/zenodo.53894). "
                "18 CSV files: daily, hourly and minute-level activity, calories, intensity, steps, METs, sleep, weight and heart rate.")
    st.dataframe(pd.DataFrame({"Source": ["dailyActivity", "sleepDay", "weightLogInfo", "hourlySteps / hourlyCalories", "minute-level + heart rate"],
        "Users": [str(N), str(S["Id"].nunique()), str(W["Id"].nunique()), str(N), "24–33"], "Used for": ["Core activity KPIs", "Sleep analysis", "Weight trends", "Hourly patterns", "SQL lab / future work"]}),
        hide_index=True, use_container_width=True)
    st.subheader("3 · Cleaning & integrity checks (SQL)")
    st.markdown("- **Nulls:** none, except `Fat` in the weight log (65 of 67 blank), so the column was dropped.\n"
                "- **Duplicates:** 543 rows in minuteSleep and 3 in sleepDay removed.\n"
                "- **Negatives:** none found.\n"
                "- **Non-wear days:** 79 full-day sedentary days (17 users) and 77 zero-step days. The sidebar toggle excludes them (on by default).\n"
                "- **Formats:** date/time strings converted to datetime; 33 user IDs appear against the 30 stated in the source.")
    st.subheader("Data limitations (ROCCC)")
    st.markdown("Small sample (33 users), 30 days, no age/sex/height, unknown distance units, dated (2016), third-party collected, "
                "only 8 users logged weight. Findings are directional.")

# =========================================================== DEEP DIVE
with t7:
    st.subheader("Steps by participant and weekday")
    hm = d.pivot_table(index=d["Id"].astype(str), columns="Weekday", values="TotalSteps", aggfunc="mean").reindex(columns=wk_order)
    fig = px.imshow(hm.sort_values("Monday", na_position="first"), aspect="auto", color_continuous_scale="Tealgrn", labels=dict(color="Avg steps"))
    st.plotly_chart(style(fig, max(380, 18 * len(hm))), use_container_width=True)
    a, b = st.columns(2)
    with a:
        st.subheader("Time in each activity level, by weekday")
        am = d.groupby("Weekday")[["LightlyActiveMinutes", "FairlyActiveMinutes", "VeryActiveMinutes"]].mean().reindex(wk_order).reset_index().melt("Weekday")
        fig = px.bar(am, x="Weekday", y="value", color="variable", barmode="group", color_discrete_sequence=[AMBER, INDIGO, TEAL], labels={"value": "Avg minutes", "variable": ""})
        st.plotly_chart(style(fig, 340), use_container_width=True)
    with b:
        st.subheader("Calories burnt by hour of day")
        ch = HC.groupby("Hour")["Calories"].mean().reset_index()
        fig = px.bar(ch, x="Hour", y="Calories", color_discrete_sequence=[INDIGO])
        st.plotly_chart(style(fig, 340), use_container_width=True)
    st.subheader("Average sedentary minutes by participant")
    sd = d.groupby(d["Id"].astype(str))["SedentaryMinutes"].mean().sort_values().reset_index()
    fig = px.bar(sd, x="SedentaryMinutes", y="Id", orientation="h", color="SedentaryMinutes", color_continuous_scale=["#38BDF8", ROSE])
    fig.update_layout(yaxis=dict(type="category"), coloraxis_showscale=False)
    st.plotly_chart(style(fig, max(340, 18 * len(sd))), use_container_width=True)
    sowhat("Activity is highly individual: a few users log 12k+ steps while many stay under 5k. "
           "Personalised goals will outperform one-size-fits-all targets.")