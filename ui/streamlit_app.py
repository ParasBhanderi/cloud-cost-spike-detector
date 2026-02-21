import io
import pandas as pd
import numpy as np
import requests
import streamlit as st

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="Cloud Cost Spike Detector (FinOps ML)", layout="wide")

# ===== Professional FinOps UI Styling =====
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] { background-color: #121826; }

    span[data-baseweb="tag"] {
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: 600;
        border-radius: 6px;
    }
    span[data-baseweb="tag"]:hover { background-color: #2563eb !important; }

    button[kind="primary"] { background-color: #4f46e5; border-radius: 8px; }

    div[data-testid="metric-container"] {
        background: #1e293b;
        padding: 12px;
        border-radius: 10px;
    }

    .stDataFrame { background-color: #111827; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Simple, clean theme tweaks
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
      .stMetric { background: rgba(255,255,255,0.04); padding: 12px; border-radius: 12px; }
      table { font-size: 14px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Page config
# ----------------------------

# Simple, clean theme tweaks (keeps your purple theme fine)
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
      .stMetric { background: rgba(255,255,255,0.04); padding: 12px; border-radius: 12px; }
      table { font-size: 14px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Cloud Cost Spike Detector (FinOps ML)")
st.caption("Upload a CSV with columns: date, service, cost")

# ----------------------------
# Sidebar (API + filters)
# ----------------------------
api_url = st.sidebar.text_input("API URL", value="http://127.0.0.1:8000")

st.sidebar.subheader("API Health")
if st.sidebar.button("Ping /health"):
    try:
        r = requests.get(f"{api_url}/health", timeout=5)
        if r.status_code == 200:
            st.sidebar.success(r.json())
        else:
            st.sidebar.error(r.text)
    except Exception as e:
        st.sidebar.error(str(e))

st.sidebar.subheader("FinOps Assumptions")
currency = st.sidebar.selectbox("Currency", ["USD ($)", "CAD ($)", "INR (₹)", "EUR (€)"], index=0)
symbol = {"USD ($)": "$", "CAD ($)": "$", "INR (₹)": "₹", "EUR (€)": "€"}[currency]

monthly_budget = st.sidebar.number_input("Monthly Budget (optional)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.subheader("View Controls")
show_service_breakdown = st.sidebar.checkbox("Show service breakdown charts", value=True)
show_anomaly_tables = st.sidebar.checkbox("Show anomaly tables", value=True)

# ----------------------------
# Upload CSV
# ----------------------------
uploaded = st.file_uploader("Upload cost CSV", type=["csv"])

if uploaded is None:
    st.info("Upload a CSV to get started.")
    st.stop()

content = uploaded.getvalue()
if not content or len(content) == 0:
    st.error("Uploaded file is empty. Please upload a valid CSV.")
    st.stop()

try:
    df = pd.read_csv(io.BytesIO(content))
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

required_cols = {"date", "service", "cost"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    st.stop()

# Normalize types
df = df.copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["service"] = df["service"].astype(str)
df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

df = df.dropna(subset=["date", "service", "cost"])
if df.empty:
    st.error("No valid rows found after parsing. Ensure date/service/cost are valid.")
    st.stop()

# Optional filters
min_d, max_d = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input("Date range", value=(min_d.date(), max_d.date()))
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df = df[(df["date"] >= start) & (df["date"] <= end)]

services = sorted(df["service"].unique().tolist())
selected_services = st.sidebar.multiselect("Services", services, default=services)
df = df[df["service"].isin(selected_services)]

if df.empty:
    st.warning("No data after filters. Adjust date range/services.")
    st.stop()

# ----------------------------
# Executive summary calculations
# ----------------------------
# Daily aggregation (total across services)
tmp = df.copy()
tmp["day"] = pd.to_datetime(tmp["date"]).dt.date

daily = (
    tmp.groupby("day", as_index=False)["cost"]
    .sum()
    .rename(columns={"cost": "daily_cost"})
)

daily["day"] = pd.to_datetime(daily["day"])

total_spend = float(daily["daily_cost"].sum())
days = int(daily["day"].nunique())
service_count = int(df["service"].nunique())

avg_daily = float(daily["daily_cost"].mean()) if days else 0.0
latest_day = daily["day"].max()
latest_spend = float(daily.loc[daily["day"] == latest_day, "daily_cost"].sum())

# Forecast (simple burn-rate forecast)
# If data spans within a month, forecast to month end. If not, still show projected monthly burn.
month_end = (latest_day + pd.offsets.MonthEnd(0)).normalize()
days_left = max((month_end - latest_day).days, 0)
forecast_eom = total_spend + (avg_daily * days_left)

def money(x: float) -> str:
    return f"{symbol}{x:,.2f}"

# ----------------------------
# Executive KPI row
# ----------------------------
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Spend (Selected)", money(total_spend))
k2.metric("Services", f"{service_count}")
k3.metric("Days", f"{days}")
k4.metric("Avg Daily Burn", money(avg_daily))
k5.metric("Forecast (EOM)", money(forecast_eom))
if monthly_budget and monthly_budget > 0:
    pct = (forecast_eom / monthly_budget) * 100.0
    k6.metric("Budget Risk", f"{pct:.0f}%", delta=f"{money(forecast_eom - monthly_budget)} vs budget")
else:
    k6.metric("Latest Day Spend", money(latest_spend))

st.divider()

# ----------------------------
# Trend charts (VP-friendly)
# ----------------------------
st.subheader("Spend Trend")
trend_df = daily.set_index("day")[["daily_cost"]].rename(columns={"daily_cost": "Daily Spend"})
st.line_chart(trend_df)

if show_service_breakdown:
    st.subheader("Service Spend Breakdown")
    by_day_service = df.copy()
    by_day_service["day"] = by_day_service["date"].dt.date
    pivot = by_day_service.pivot_table(index="day", columns="service", values="cost", aggfunc="sum", fill_value=0.0)
    pivot.index = pd.to_datetime(pivot.index)
    st.area_chart(pivot)

# ----------------------------
# Top services table
# ----------------------------
st.subheader("Top Services by Spend")
svc = df.groupby("service", as_index=False)["cost"].sum().sort_values("cost", ascending=False)
svc["share_pct"] = (svc["cost"] / max(total_spend, 1e-9)) * 100.0

# Add a bit more business context
last_day = df[df["date"].dt.date == latest_day.date()]
last_day_svc = last_day.groupby("service", as_index=False)["cost"].sum().rename(columns={"cost": "last_day_cost"})

svc = svc.merge(last_day_svc, on="service", how="left").fillna({"last_day_cost": 0.0})
svc["avg_daily_cost"] = svc["cost"] / max(days, 1)
svc = svc.rename(columns={"cost": "total_cost"})

svc_display = svc.copy()
svc_display["total_cost"] = svc_display["total_cost"].map(money)
svc_display["avg_daily_cost"] = svc_display["avg_daily_cost"].map(money)
svc_display["last_day_cost"] = svc_display["last_day_cost"].map(money)
svc_display["share_pct"] = svc_display["share_pct"].map(lambda x: f"{x:.1f}%")

st.dataframe(svc_display, use_container_width=True, hide_index=True)

st.divider()

# ----------------------------
# Detect anomalies (API)
# ----------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Spike Detection (API)")
    if st.button("Detect anomalies"):
        try:
            files = {"file": ("costs.csv", content, "text/csv")}
            r = requests.post(f"{api_url}/detect", files=files, timeout=30)
            if r.status_code != 200:
                st.error(r.text)
            else:
                data = r.json()
                anomalies = pd.DataFrame(data.get("anomalies", []))
                st.success(f"Detected {data.get('total_anomalies', 0)} anomalies across {data.get('total_rows', 0)} rows.")

                if not anomalies.empty and show_anomaly_tables:
                    # Make it business-friendly
                    # Expected columns from your pipeline: date, service, cost, anomaly_score, cost_pct_change, cost_rolling_mean_7
                    for c in ["cost", "cost_rolling_mean_7", "cost_pct_change"]:
                        if c in anomalies.columns:
                            anomalies[c] = pd.to_numeric(anomalies[c], errors="coerce")

                    if "date" in anomalies.columns:
                        anomalies["date"] = pd.to_datetime(anomalies["date"], errors="coerce")

                    # Add impact estimate (how much above baseline)
                    if "cost_rolling_mean_7" in anomalies.columns and "cost" in anomalies.columns:
                        anomalies["estimated_impact"] = (anomalies["cost"] - anomalies["cost_rolling_mean_7"]).clip(lower=0)
                    else:
                        anomalies["estimated_impact"] = np.nan

                    # Sort: most expensive spikes first
                    sort_col = "estimated_impact" if "estimated_impact" in anomalies.columns else "cost"
                    anomalies = anomalies.sort_values(sort_col, ascending=False)

                    # Pretty display
                    disp = anomalies.copy()
                    if "cost" in disp.columns:
                        disp["cost"] = disp["cost"].map(lambda x: money(float(x)) if pd.notna(x) else "")
                    if "cost_rolling_mean_7" in disp.columns:
                        disp["cost_rolling_mean_7"] = disp["cost_rolling_mean_7"].map(lambda x: money(float(x)) if pd.notna(x) else "")
                    if "estimated_impact" in disp.columns:
                        disp["estimated_impact"] = disp["estimated_impact"].map(lambda x: money(float(x)) if pd.notna(x) else "")
                    if "cost_pct_change" in disp.columns:
                        disp["cost_pct_change"] = disp["cost_pct_change"].map(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "")

                    keep = [c for c in ["date", "service", "cost", "cost_rolling_mean_7", "cost_pct_change", "anomaly_score", "estimated_impact"] if c in disp.columns]
                    st.dataframe(disp[keep], use_container_width=True, hide_index=True)

                    # Executive takeaway
                    if "estimated_impact" in anomalies.columns:
                        impact_total = float(pd.to_numeric(anomalies["estimated_impact"], errors="coerce").fillna(0).sum())
                        st.info(f"Estimated anomaly impact (above baseline): **{money(impact_total)}**")

                    # Recommended actions (simple but VP-friendly)
                    st.subheader("Recommended Actions")
                    top_service = anomalies["service"].iloc[0] if "service" in anomalies.columns else None
                    st.markdown(
                        f"""
- Investigate **{top_service or "top service"}** spike: check scaling events, new deployments, node group changes, and pricing model (On-Demand vs Spot).
- Validate tag hygiene: ensure costs are attributable to team, env, and workload (FinOps chargeback).
- Review rightsizing and idle resources (underutilized instances, orphaned disks, overprovisioned nodes).
"""
                    )

                    # Download
                    csv_bytes = anomalies.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download anomalies CSV",
                        data=csv_bytes,
                        file_name="anomalies.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No anomalies returned (or anomaly table display disabled).")
        except Exception as e:
            st.error(f"Detect request failed: {e}")

with col2:
    st.subheader("Executive Summary (API)")
    if st.button("Summary"):
        try:
            files = {"file": ("costs.csv", content, "text/csv")}
            r = requests.post(f"{api_url}/detect/summary", files=files, timeout=30)
            if r.status_code != 200:
                st.error(r.text)
            else:
                summary = r.json()
                st.json(summary)
        except Exception as e:
            st.error(f"Summary request failed: {e}")

# ----------------------------
# Raw preview (still useful)
# ----------------------------
with st.expander("Raw Data Preview", expanded=False):
    preview = df.copy()
    preview = preview.sort_values("date")
    preview["cost"] = preview["cost"].map(lambda x: money(float(x)))
    st.dataframe(preview.head(200), use_container_width=True, hide_index=True)