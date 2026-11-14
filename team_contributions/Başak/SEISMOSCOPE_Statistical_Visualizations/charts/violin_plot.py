
"""SEISMOSCOPE | Violin Plot Visualization.

Compares reported earthquake magnitude uncertainty
across different magnitude estimation methods.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Shared visual theme
PLOT_BACKGROUND = "#F3F7F9"
TEXT_COLOR = "#253C4D"
GRID_COLOR = "#D6E1E7"


METHOD_COLORS = {
    "mb": "#0D9488",
    "mww": "#6366F1",
    "mwr": "#D97706",
}



def create_violin_plot(
    df: pd.DataFrame,
    methods: list[str]
) -> go.Figure:
    """
    Compare magnitude uncertainty distributions
    for the selected estimation methods.

    Returns a Plotly Figure.
    """

    required = {"magType", "magError"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    valid = df.loc[
        df["magType"].isin(methods),
        ["magType", "magError"]
    ].copy()

    valid["magError"] = pd.to_numeric(
        valid["magError"],
        errors="coerce"
    )

    valid = valid.dropna(subset=["magError"])
    valid = valid.loc[valid["magError"] >= 0]

    if valid.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No valid measurements match the selected filters.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                color=TEXT_COLOR,
                size=15
            )
        )

    else:

        fig = px.violin(
            valid,
            x="magType",
            y="magError",
            color="magType",
            category_orders={
                "magType": methods
            },
            color_discrete_map=METHOD_COLORS,
            box=True,
            points=False
        )

        fig.update_traces(
            spanmode="hard",
            opacity=0.77,
            line_width=1.2,
            box_visible=True
        )

    fig.update_layout(
        height=470,
        paper_bgcolor=PLOT_BACKGROUND,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=13
        ),
        margin=dict(
            l=30,
            r=20,
            t=20,
            b=50
        ),
        showlegend=False,
        hovermode="closest"
    )

    fig.update_xaxes(
        title="Magnitude estimation method",
        gridcolor=GRID_COLOR
    )

    fig.update_yaxes(
        title="Reported magnitude uncertainty (magError)",
        gridcolor=GRID_COLOR,
        rangemode="tozero"
    )

    return fig
