
"""SEISMOSCOPE | Shared Plotly Chart Style."""
import plotly.graph_objects as go


CHART_PALETTE = [
    "#0D9488",  # Teal
    "#6366F1",  # Indigo
    "#D97706",  # Amber
    "#EC4899",  # Pink
]


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
