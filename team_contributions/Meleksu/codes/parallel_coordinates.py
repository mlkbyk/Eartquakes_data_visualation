# ==============================================================================
#parallel_coordinates.py
# Description: Parallel Coordinates plot for multidimensional earthquake 
#              analysis across magnitude, depth, and measurement quality metrics.
# ==============================================================================

import pandas as pd
import plotly.graph_objects as go

# Load the prepared earthquake dataset
df = pd.read_csv("earthquakes_dashboard_ready.csv")

# Define the columns required for multidimensional analysis
columns = [
    "mag",
    "depth",
    "rms",
    "gap",
    "nst",
    "magError"
]

# Remove rows with missing values in the selected columns
parallel_df = df[columns].dropna().copy()

print("Original records:", len(df))
print("Records used:", len(parallel_df))
print("Removed records:", len(df) - len(parallel_df))

# Build the Parallel Coordinates figure
fig = go.Figure(
    data=go.Parcoords(
        line=dict(
            color=parallel_df["mag"],
            colorscale=[
                [0, "#24476B"],
                [0.35, "#4C789A"],
                [0.65, "#F4C66A"],
                [1, "#E87555"]
            ],
            cmin=parallel_df["mag"].min(),
            cmax=parallel_df["mag"].max(),
            colorbar=dict(title="Magnitude"),
            showscale=True
        ),
        dimensions=[
            dict(
                label="Magnitude",
                values=parallel_df["mag"]
            ),
            dict(
                label="Depth (km)",
                values=parallel_df["depth"]
            ),
            dict(
                label="RMS",
                values=parallel_df["rms"]
            ),
            dict(
                label="Azimuthal Gap",
                values=parallel_df["gap"]
            ),
            dict(
                label="Number of Stations",
                values=parallel_df["nst"]
            ),
            dict(
                label="Magnitude Error",
                values=parallel_df["magError"]
            )
        ]
    )
)

# Configure layout, title, and margins
fig.update_layout(
    title=dict(
        text=(
            "Multidimensional Earthquake Analysis"
            "<br><sup>Magnitude, Depth and Measurement Quality</sup>"
        ),
        x=0.5
    ),
    template="plotly_white",
    height=700,
    margin=dict(l=100, r=100, t=110, b=70),
    font=dict(family="Arial", size=12)
)

fig.show()
