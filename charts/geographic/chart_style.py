
"""SEISMOSCOPE | Shared Plotly Chart Style."""

import plotly.graph_objects as go


# --------------------------------------------------
# ORIGINAL DASHBOARD PALETTE
# --------------------------------------------------

CHART_PALETTE = [
    "#0D9488",  # Teal
    "#6366F1",  # Indigo
    "#D97706",  # Amber
    "#EC4899",  # Pink
]


# --------------------------------------------------
# GEOGRAPHIC MAP & SUNBURST COLOR SCALE
# Purple -> Blue -> Green -> Yellow -> Orange -> Red
# --------------------------------------------------

GEOGRAPHIC_MAG_SCALE = [
    [0.00, "#5E4FA2"],  # Purple
    [0.20, "#3288BD"],  # Blue
    [0.40, "#66C2A5"],  # Teal / Green
    [0.60, "#E6F598"],  # Yellow-green
    [0.80, "#FDAE61"],  # Orange
    [1.00, "#9E0142"],  # Dark red
]

SUNBURST_MAG_SCALE = GEOGRAPHIC_MAG_SCALE


# --------------------------------------------------
# SANKEY DIAGRAM COLOR PALETTE
# --------------------------------------------------

# Magnitude categories
SANKEY_MAG_COLORS = {
    "light": "#0EA5E9",       # Blue
    "moderate": "#EAB308",    # Yellow
    "strong": "#F97316",      # Orange
    "major": "#E11D48",       # Red
}

# Depth categories
SANKEY_DEPTH_COLORS = {
    "shallow": "#10B981",         # Green
    "intermediate": "#8B5CF6",   # Purple
    "deep": "#6366F1",           # Indigo
}

# Hemisphere categories
SANKEY_HEMISPHERE_COLORS = {
    "southern": "#EC4899",  # Pink
    "northern": "#14B8A6",  # Teal
}


def hex_to_rgba(hex_color: str, alpha: float = 0.35) -> str:
    """
    Convert a hex color into an RGBA string
    for transparent Sankey links.
    """

    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r},{g},{b},{alpha})"


# --------------------------------------------------
# ORIGINAL CLEAN CHART STYLE
# --------------------------------------------------

def apply_clean_chart_style(fig: go.Figure) -> go.Figure:
    """
    Apply a consistent chart theme without
    changing data, axes ranges, or calculations.
    """

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Arial, sans-serif",
            color="#334155",
            size=12
        ),

        hoverlabel=dict(
            bgcolor="#0F172A",
            font_color="#FFFFFF",
            bordercolor="#0F172A"
        ),

        colorway=CHART_PALETTE
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#CBD5E1",
        tickfont=dict(color="#64748B"),
        title_font=dict(
            color="#475569",
            size=13
        )
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F1F5F9",
        zeroline=False,
        linecolor="#CBD5E1",
        tickfont=dict(color="#64748B"),
        title_font=dict(
            color="#475569",
            size=13
        )
    )

    return fig
