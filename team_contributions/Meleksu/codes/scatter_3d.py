# ==============================================================================
# File Name:scatter_3d.py
# Description: 3D Scatter Plots of global earthquake distribution comparing 
#              datasets with and without fixed 10km depth records.
# ==============================================================================

import pandas as pd
import plotly.express as px

# Load the prepared earthquake dataset
df = pd.read_csv("earthquakes_dashboard_ready.csv")

# Select spatial and magnitude columns and drop missing records
columns_3d = ["latitude", "longitude", "depth", "mag", "place"]
scatter_df = df[columns_3d].dropna().copy()

# ------------------------------------------------------------------------------
# Plot 1: 3D Scatter Plot (show_10km = True)
# ------------------------------------------------------------------------------

show_10km = True

if show_10km:
    display_df = scatter_df.copy()
else:
    display_df = scatter_df[scatter_df["depth"] != 10].copy()

print("Displayed records (show_10km=True):", len(display_df))

fig_with_10km = px.scatter_3d(
    display_df,
    x="longitude",
    y="latitude",
    z="depth",
    color="mag",
    hover_name="place",
    hover_data=["latitude", "longitude", "depth", "mag"],
    color_continuous_scale="RdYlBu_r",
    title="3D Global Earthquake Distribution"
)

fig_with_10km.update_traces(
    marker=dict(size=3, opacity=0.75)
)

fig_with_10km.update_layout(
    template="plotly_white",
    height=750,
    scene=dict(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        zaxis_title="Depth (km)",
        zaxis=dict(autorange="reversed")
    )
)

fig_with_10km.show()

# ------------------------------------------------------------------------------
# Plot 2: 3D Scatter Plot (show_10km = False)
# ------------------------------------------------------------------------------

show_10km = False

if show_10km:
    display_df = scatter_df.copy()
else:
    display_df = scatter_df[scatter_df["depth"] != 10].copy()

print("Displayed records (show_10km=False):", len(display_df))

fig_without_10km = px.scatter_3d(
    display_df,
    x="longitude",
    y="latitude",
    z="depth",
    color="mag",
    hover_name="place",
    hover_data=["latitude", "longitude", "depth", "mag"],
    color_continuous_scale="RdYlBu_r",
    title="3D Global Earthquake Distribution"
)

fig_without_10km.update_traces(
    marker=dict(size=3, opacity=0.75)
)

fig_without_10km.update_layout(
    template="plotly_white",
    height=750,
    scene=dict(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        zaxis_title="Depth (km)",
        zaxis=dict(autorange="reversed")
    )
)

fig_without_10km.show()
