
"""Member 1 — hierarchical earthquake categories, adapted from combined app.py."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from charts.geographic.chart_style import SUNBURST_MAG_SCALE


def create_sunburst(data: pd.DataFrame) -> go.Figure:
    """Show Hemisphere → Magnitude band → Depth category, color=mean magnitude."""

    required = {
        "latitude_hemisphere",
        "magnitude_band",
        "depth_category",
        "mag"
    }

    missing = required.difference(data.columns)

    if missing:
        raise ValueError(f"Sunburst requires: {sorted(missing)}")

    valid = data.dropna(subset=list(required)).copy()

    if valid.empty:
        fig = go.Figure()

        fig.add_annotation(
            text="No earthquake records match these filters.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False
        )

        fig.update_layout(height=500)

        return fig

    # --------------------------------------------------
    # SUNBURST CHART
    # Original hierarchy and calculations preserved.
    # Only the magnitude color scale is changed.
    # --------------------------------------------------

    fig = px.sunburst(
        valid,
        path=[
            "latitude_hemisphere",
            "magnitude_band",
            "depth_category"
        ],
        color="mag",
        color_continuous_scale=SUNBURST_MAG_SCALE,
        height=520,
        labels={
            "mag": "Average magnitude (M)"
        }
    )

    # --------------------------------------------------
    # ORIGINAL HOVER INFORMATION
    # --------------------------------------------------

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Records: %{value:,}<br>"
            "Mean magnitude: %{color:.2f} M<br>"
            "Parent share: %{percentParent:.1%}"
            "<extra></extra>"
        ),
        insidetextorientation="radial"
    )

    # --------------------------------------------------
    # ORIGINAL LAYOUT
    # --------------------------------------------------

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=45,
            b=10
        ),
        title="Hierarchical earthquake record distribution"
    )

    return fig
