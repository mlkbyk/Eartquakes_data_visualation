# ==============================================================================
# File Name: member2_treemap.py
# Description: Treemap visualizations showing global earthquake distribution 
#              and average magnitude across the top 15 locations.
# ==============================================================================

import pandas as pd
import plotly.express as px

# Load the prepared earthquake dataset
df = pd.read_csv("earthquakes_dashboard_ready.csv")
print("Dataset Shape:", df.shape)

# ------------------------------------------------------------------------------
# Part A: Initial Treemap - Earthquake Records by Location
# ------------------------------------------------------------------------------

# Select required columns and remove missing values
data = df[["place", "mag", "id"]].dropna().copy()

# Group by location to calculate earthquake count and average magnitude
summary = (
    data.groupby("place")
    .agg(
        earthquake_count=("id", "count"),
        avg_magnitude=("mag", "mean")
    )
    .reset_index()
)

# Select the top 15 locations with the highest earthquake records
summary_top15 = summary.sort_values(
    "earthquake_count",
    ascending=False
).head(15)

# Create the initial Treemap
fig_initial = px.treemap(
    summary_top15,
    path=["place"],
    values="earthquake_count",
    color="avg_magnitude",
    color_continuous_scale="RdYlBu_r",
    hover_data={
        "earthquake_count": True,
        "avg_magnitude": ":.2f"
    },
    title="Earthquake Records by Location"
)

fig_initial.update_layout(
    template="plotly_white",
    height=650,
    title_x=0.5
)

fig_initial.show()

# ------------------------------------------------------------------------------
# Part B: Final Custom Treemap - Global Earthquake Distribution by Location
# ------------------------------------------------------------------------------

# Check for null values in target columns
print(df[["place", "mag", "id"]].isnull().sum())

# Group dataset by location and sort descending
summary_final = (
    df.groupby("place")
    .agg(
        earthquake_count=("id", "count"),
        avg_magnitude=("mag", "mean")
    )
    .reset_index()
    .sort_values("earthquake_count", ascending=False)
)

# Create the customized final Treemap with a custom color scale
fig_final = px.treemap(
    summary_final.head(15),
    path=["place"],
    values="earthquake_count",
    color="avg_magnitude",
    color_continuous_scale=[
        "#24476B",
        "#4C789A",
        "#F4C66A",
        "#E87555"
    ],
    hover_data={
        "earthquake_count": True,
        "avg_magnitude": ":.2f"
    },
    title="Global Earthquake Distribution by Location"
)

# Customize hover details and white cell borders
fig_final.update_traces(
    textinfo="label+value",
    marker=dict(
        line=dict(color="white", width=2)
    ),
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Earthquake Count: %{value}<br>"
        "Average Magnitude: %{color:.2f}"
        "<extra></extra>"
    )
)

fig_final.update_layout(
    template="plotly_white",
    height=700,
    title_x=0.5,
    title_font_size=23,
    margin=dict(t=80, l=20, r=20, b=20)
)

fig_final.show()
