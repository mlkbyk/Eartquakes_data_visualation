
"""SEISMOSCOPE | Statistical and Temporal Visualizations.

Two complementary Density Contour views of the same filtered USGS events.
"""

import pandas as pd
import plotly.graph_objects as go


PLOT_BG = "#F3F7F9"
TEXT = "#253C4D"
GRID = "#D6E1E7"


DENSITY_COLORS = [
    [0.00, "#FFFFFF"],
    [0.12, "#D9EDEC"],
    [0.35, "#A4D5D3"],
    [0.58, "#5BAFB8"],
    [0.80, "#287E98"],
    [1.00, "#194C70"],
]



def _density_contour(
    df: pd.DataFrame,
    view: str,
    detailed: bool
) -> go.Figure:

    """Create a histogram-based 2D density contour.

    Overview uses Plotly's automatic bin widths.
    Detailed uses fixed, narrower bin widths.
    Neither view uses kernel density estimation (KDE).
    """

    needed = {"mag", "depth"}
    missing = needed - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    valid = df.dropna(subset=["mag", "depth"])

    fig = go.Figure()

    if not valid.empty:

        options = dict(
            x=valid["mag"],
            y=valid["depth"],
            colorscale=DENSITY_COLORS,
            ncontours=16,

            contours=dict(
                coloring="fill",
                showlabels=False
            ),

            line=dict(
                color="rgba(38, 83, 103, 0.45)",
                width=0.7
            ),

            colorbar=dict(
                title=dict(text="Events / bin"),
                thickness=13,
                len=0.78
            ),

            hovertemplate=(
                "Magnitude bin: %{x:.2f}<br>"
                "Depth bin: %{y:.0f} km<br>"
                "Events / bin: %{z}<extra></extra>"
            ),

            name="Earthquake concentration"
        )

        if detailed:

            options["xbins"] = dict(
                start=4.45,
                end=7.85,
                size=0.05
            )

            options["ybins"] = dict(
                start=-10,
                end=760,
                size=10
            )

        fig.add_trace(
            go.Histogram2dContour(**options)
        )

    else:

        fig.add_annotation(
            text="No records match the selected filters.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=15, color=TEXT)
        )

    # Display ranges change only the visible chart area.

    if view == "Focused View":
        x_limits = [4.45, 6.05]
        y_limits = [0, 150]

    elif view == "Full Range":
        x_limits = [4.45, 7.85]
        y_limits = [-10, 750]

    else:
        raise ValueError(
            "view must be 'Focused View' or 'Full Range'"
        )

    fig.update_layout(
        height=490,

        margin=dict(
            l=45,
            r=20,
            t=20,
            b=55
        ),

        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,

        font=dict(
            family="Arial, sans-serif",
            color=TEXT,
            size=13
        ),

        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_color=TEXT
        ),

        dragmode="zoom",
        showlegend=False
    )

    fig.update_xaxes(
        title="Earthquake magnitude (M)",
        range=x_limits,
        gridcolor=GRID,
        zeroline=False,
        linecolor=GRID
    )

    fig.update_yaxes(
        title="Hypocentral depth (km)",
        range=y_limits,
        gridcolor=GRID,
        zeroline=False,
        linecolor=GRID
    )

    return fig


def create_density_contour_smoothed(
    df: pd.DataFrame,
    view: str = "Focused View"
) -> go.Figure:

    """Overview with automatically selected histogram bins."""

    return _density_contour(
        df,
        view=view,
        detailed=False
    )


def create_density_contour_binned(
    df: pd.DataFrame,
    view: str = "Focused View"
) -> go.Figure:

    """Detailed contour using fixed fine histogram bins."""

    return _density_contour(
        df,
        view=view,
        detailed=True
    )
