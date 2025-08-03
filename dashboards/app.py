import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import numpy as np

# ─── 1. Load data ─────────────────────────────────────────────

# ─── Resolve paths ─────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
RAW_DIR   = BASE_DIR / "data" / "raw"
PROC_DIR  = BASE_DIR / "data" / "processed"

# ─── Find all cities by processed CSV filenames ───────────────
cities = [p.stem for p in PROC_DIR.glob("*.csv")]

# Graceful error if no data
if not cities:
    st.error(f"❌ No processed data found in `{PROC_DIR}`. "
             "Run `python src/pipeline.py` locally and commit the results.")
    st.stop()

@st.cache_data
def load_city_data(city_slug):
    """
    Reads the cleaned & merged CSV from data/processed/.
    """
    path = PROC_DIR / f"{city_slug}.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df

data = {city: load_city_data(city) for city in cities}

# ─── 2. Sidebar Controls ──────────────────────────────────────
st.sidebar.title("Controls")
min_date = min(df["date"].min() for df in data.values())
max_date = max(df["date"].max() for df in data.values())
date_range = st.sidebar.date_input(
    "Date range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
sel_cities = st.sidebar.multiselect("Cities", cities, default=cities)


# Filter data by sidebar selections
filtered = {
    city: df.loc[
        (df["date"] >= pd.to_datetime(date_range[0])) &
        (df["date"] <= pd.to_datetime(date_range[1]))
    ]
    for city, df in data.items() if city in sel_cities
}

# ─── 3. City Coordinates (for the map) ────────────────────────
city_coords = {
    "new_york": {"lat": 40.7128, "lon": -74.0060},
    "chicago":  {"lat": 41.8781, "lon": -87.6298},
    "houston":  {"lat": 29.7604, "lon": -95.3698},
    "phoenix":  {"lat": 33.4484, "lon": -112.0740},
    "seattle":  {"lat": 47.6062, "lon": -122.3321},
}

# ─── 4. Page Title & Placeholders ────────────────────────────
st.title("US Weather & Energy Dashboard")
st.markdown(f"_Last updated: {max_date.date()}_")

st.header("1. Geographic Overview")
map_placeholder = st.empty()

st.header("2. Time Series Analysis")
ts_placeholder  = st.empty()

st.header("3. Correlation Analysis")
corr_placeholder = st.empty()

st.header("4. Usage Patterns Heatmap")
heat_placeholder = st.empty()


# ─── 5. Visualization 1: Geographic Overview 

# Build a DataFrame of one row per city with latest stats
map_rows = []
for city, df in filtered.items():
    # Sort by date to get latest and yesterday
    df_sorted = df.sort_values("date")
    latest    = df_sorted.iloc[-1]
    yesterday = df_sorted.iloc[-2]
    pct_chg   = (latest.demand - yesterday.demand) / yesterday.demand * 100

    map_rows.append({
        "City":     city.replace("_", " ").title(),
        "Latitude": city_coords[city]["lat"],
        "Longitude":city_coords[city]["lon"],
        "Temp (°F)":round(latest.TMAX,1),
        "Demand":   int(latest.demand),
        "% Change": round(pct_chg,1),
        "Trend":    "Up" if pct_chg > 0 else "Down"
    })

map_df = pd.DataFrame(map_rows)

# Create a U.S. map
fig_geo = px.scatter_geo(
    map_df,
    lat="Latitude",
    lon="Longitude",
    scope="usa",
    color="Trend",
    color_discrete_map={"Up":"red","Down":"green"},
    size="Demand",
    size_max=30,
    hover_name="City",
    hover_data={
        "Temp (°F)": True,
        "Demand": True,
        "% Change": True
    },
    title="Current Temperature & Energy Demand by City"
)

# Render into the placeholder
map_placeholder.plotly_chart(fig_geo, use_container_width=True)



# ─── 6. Visualization 2: Dual-Axis Time Series (corrected) ───────────────

# Ensure ts_city is chosen from sel_cities only:
ts_city = st.sidebar.selectbox("Time Series: select city", sel_cities, index=0)

# Grab & sort the data for the selected city
df_ts = filtered[ts_city].copy().sort_values("date")

# Build the figure
fig_ts = go.Figure()

# 1) Temperature on left axis
fig_ts.add_trace(go.Scatter(
    x=df_ts["date"],
    y=df_ts["TMAX"],
    mode="lines",
    name="Temperature",
    yaxis="y1"
))

# 2) Energy on right axis (dotted)
fig_ts.add_trace(go.Scatter(
    x=df_ts["date"],
    y=df_ts["demand"],
    mode="lines",
    name="Energy Usage",
    line=dict(dash="dot"),
    yaxis="y2"
))

# 3) Shade weekends
week_starts = pd.date_range(
    start=df_ts["date"].min(),
    end=df_ts["date"].max(),
    freq="W-SAT"
)
for ws in week_starts:
    fig_ts.add_vrect(
        x0=ws,
        x1=ws + timedelta(days=1),
        fillcolor="lightgrey",
        opacity=0.3,
        layer="below",
        line_width=0
    )

# 4) Layout with dual axes
fig_ts.update_layout(
    xaxis=dict(title="Date"),
    yaxis=dict(title="Temperature (°F)", side="left"),
    yaxis2=dict(
        title="Energy Usage",
        side="right",
        overlaying="y"
    ),
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=50, r=50, t=50, b=50)
)

# Render into placeholder
ts_placeholder.plotly_chart(fig_ts, use_container_width=True)

# ─── 7. Visualization 3: Correlation Analysis ─────────────────────

# 1) Combine all selected cities into one DataFrame
df_corr = pd.concat(
    [df.assign(city=city.replace("_"," ").title()) for city, df in filtered.items()],
    ignore_index=True
)

# 2) Compute regression parameters & R²
x = df_corr["TMAX"]
y = df_corr["demand"]
slope, intercept = np.polyfit(x, y, 1)
r = np.corrcoef(x, y)[0,1]
r2 = r**2

# 3) Build base scatter
fig_corr = go.Figure()
for city in df_corr["city"].unique():
    sub = df_corr[df_corr["city"] == city]
    fig_corr.add_trace(go.Scatter(
        x=sub["TMAX"],
        y=sub["demand"],
        mode="markers",
        name=city,
        hovertemplate=
          "<b>%{text}</b><br>Temp: %{x:.1f}°F<br>Energy: %{y:.0f}<br>Date: %{customdata[0]|%Y-%m-%d}",
        text=[city]*len(sub),
        customdata=sub[["date"]].values
    ))

# 4) Add regression line
x_line = np.linspace(x.min(), x.max(), 100)
y_line = slope * x_line + intercept
fig_corr.add_trace(go.Scatter(
    x=x_line, y=y_line,
    mode="lines",
    name="Fit: y=mx+b",
    line=dict(color="black")
))

# 5) Annotate equation & R²
eq_text = f"y = {slope:.2f}·x + {intercept:.0f}<br>R² = {r2:.2f}"
fig_corr.add_annotation(
    x=0.05, y=0.95, xref="paper", yref="paper",
    text=eq_text,
    showarrow=False,
    bgcolor="rgba(255,255,255,0.7)",
    bordercolor="black"
)

# 6) Layout
fig_corr.update_layout(
    title="Correlation: Temperature vs. Energy Consumption",
    xaxis=dict(title="Temperature (°F)"),
    yaxis=dict(title="Energy Usage"),
    legend=dict(title="City"),
    margin=dict(l=50, r=50, t=50, b=50)
)

# 7) Render
corr_placeholder.plotly_chart(fig_corr, use_container_width=True)

# ─── 8. Visualization 4: Usage Patterns Heatmap ─────────────────

# Select which city to show on the heatmap
hm_city = st.sidebar.selectbox("Heatmap: select city", sel_cities, index=0)

# Subset & prepare data
df_h = filtered[hm_city].copy()
df_h["temp_avg"] = (df_h["TMAX"] + df_h["TMIN"]) / 2
df_h["weekday"]  = df_h["date"].dt.day_name()

# Bin temperatures
bin_edges  = [float("-inf"), 50, 60, 70, 80, 90, float("inf")]
bin_labels = ["<50°F", "50-60°F", "60-70°F", "70-80°F", "80-90°F", ">90°F"]
df_h["temp_bin"] = pd.cut(df_h["temp_avg"], bins=bin_edges, labels=bin_labels)

# Compute average demand per (temp_bin, weekday)
pivot = (
    df_h
    .groupby(["temp_bin","weekday"])["demand"]
    .mean()
    .reset_index()
    .pivot(index="temp_bin", columns="weekday", values="demand")
)

# Ensure consistent ordering
weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
pivot = pivot.reindex(index=bin_labels, columns=weekdays)

# Build the heatmap
fig_heat = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=weekdays,
    y=bin_labels,
    colorscale=[[0,"blue"],[1,"red"]],
    colorbar=dict(title="Avg Demand"),
    text=pivot.round(1).values,
    texttemplate="%{text}",
    hovertemplate="Temp Range: %{y}<br>Day: %{x}<br>Avg Demand: %{z:.1f}<extra></extra>"
))

fig_heat.update_layout(
    title=f"Average Energy Usage by Temp & Day ({hm_city.replace('_',' ').title()})",
    xaxis_nticks=7, yaxis_nticks=6,
    margin=dict(l=50, r=50, t=50, b=50)
)

# Render into placeholder
heat_placeholder.plotly_chart(fig_heat, use_container_width=True)
