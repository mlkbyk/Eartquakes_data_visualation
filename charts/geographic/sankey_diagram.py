
"""Member 1 — categorical earthquake Sankey diagram from combined app.py.

The bands are categorical transitions, NOT physical event flows or movement.
"""

import pandas as pd
import plotly.graph_objects as go

from charts.geographic.chart_style import (
    SANKEY_MAG_COLORS,
    SANKEY_DEPTH_COLORS,
    SANKEY_HEMISPHERE_COLORS,
    hex_to_rgba,
)


# --------------------------------------------------
# SANKEY CATEGORIES
# --------------------------------------------------

CATEGORIES = (
    "magnitude_band",
    "depth_category",
    "latitude_hemisphere"
)


# --------------------------------------------------
# CATEGORY COLORS
# Based on Member 1's original colorful Sankey.
# --------------------------------------------------

COLOR = {
    # Magnitude: blue, yellow, orange, red
    "M4.5": SANKEY_MAG_COLORS["light"],
    "M5.0": SANKEY_MAG_COLORS["moderate"],
    "M6.0": SANKEY_MAG_COLORS["strong"],
    "M7.0": SANKEY_MAG_COLORS["major"],

    # Depth: green, purple, indigo
    "Shallow": SANKEY_DEPTH_COLORS["shallow"],
    "Intermediate": SANKEY_DEPTH_COLORS["intermediate"],
    "Deep": SANKEY_DEPTH_COLORS["deep"],

    # Hemisphere: teal and pink
    "Northern": SANKEY_HEMISPHERE_COLORS["northern"],
    "Southern": SANKEY_HEMISPHERE_COLORS["southern"],
}


def _color(label: str) -> str:
    """Return the corresponding color for a category label."""

    return next(
        (
            value
            for prefix, value in COLOR.items()
            if str(label).startswith(prefix)
        ),
        "#94A3B8"
    )


def create_sankey_diagram(data: pd.DataFrame) -> go.Figure:
    """Build magnitude band → depth category → hemisphere count-flow Sankey."""

    missing = set(CATEGORIES).difference(data.columns)

    if missing:
        raise ValueError(f"Sankey requires: {sorted(missing)}")

    valid = data.dropna(
        subset=list(CATEGORIES)
    ).copy()

    fig = go.Figure()

    if valid.empty:
        fig.add_annotation(
            text="No earthquake records match these filters.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False
        )
        fig.update_layout(height=490)
        return fig

    # --------------------------------------------------
    # ORIGINAL DATA AGGREGATION - UNCHANGED
    # --------------------------------------------------

    first = (
        valid.groupby(
            [CATEGORIES[0], CATEGORIES[1]],
            observed=True
        )
        .size()
        .reset_index(name="value")
    )

    second = (
        valid.groupby(
            [CATEGORIES[1], CATEGORIES[2]],
            observed=True
        )
        .size()
        .reset_index(name="value")
    )

    # Namespaced node IDs avoid conflating equal
    # labels in different stages.

    node_ids = []
    names = []

    for stage, field in enumerate(CATEGORIES):
        for label in sorted(valid[field].astype(str).unique()):
            node_ids.append((stage, label))
            names.append(label)

    lookup = {
        key: idx
        for idx, key in enumerate(node_ids)
    }

    sources = []
    targets = []
    values = []
    colors = []

    # --------------------------------------------------
    # LINKS
    # Original transitions are preserved.
    # Only the link colors are updated.
    # --------------------------------------------------

    for stage, table in [(0, first), (1, second)]:

        left = CATEGORIES[stage]
        right = CATEGORIES[stage + 1]

        for _, item in table.iterrows():

            source_label = str(item[left])
            target_label = str(item[right])

            sources.append(
                lookup[(stage, source_label)]
            )

            targets.append(
                lookup[(stage + 1, target_label)]
            )

            values.append(
                int(item["value"])
            )

            # Color each link according to its source.
            # Stage 0: magnitude category colors.
            # Stage 1: depth category colors.

            source_color = _color(source_label)

            if stage == 0:
                colors.append(
                    hex_to_rgba(source_color, 0.35)
                )
            else:
                colors.append(
                    hex_to_rgba(source_color, 0.40)
                )

    # --------------------------------------------------
    # SANKEY DIAGRAM
    # --------------------------------------------------

    fig.add_trace(
        go.Sankey(
            node=dict(
                label=names,
                color=[
                    _color(label)
                    for label in names
                ],
                pad=19,
                thickness=18,
                line=dict(
                    color="#FFFFFF",
                    width=1.2
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Recorded events: %{value:,}"
                    "<extra></extra>"
                )
            ),

            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate=(
                    "%{source.label} → %{target.label}<br>"
                    "Count: %{value:,}"
                    "<extra></extra>"
                )
            )
        )
    )

    # --------------------------------------------------
    # ORIGINAL LAYOUT
    # --------------------------------------------------

    fig.update_layout(
        height=500,
        margin=dict(
            l=12,
            r=12,
            t=48,
            b=12
        ),
        title="Magnitude band → Depth category → Hemisphere",
        font=dict(size=12)
    )

    return fig
