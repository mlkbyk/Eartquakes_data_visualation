"""Member 1 — categorical earthquake Sankey diagram from combined app.py.

The bands are categorical transitions, NOT physical event flows or movement.
"""
import pandas as pd
import plotly.graph_objects as go

CATEGORIES = ("magnitude_band", "depth_category", "latitude_hemisphere")
COLOR = {"M4.5": "#0D9488", "M5.0": "#6366F1", "M6.0": "#D97706",
         "M7.0": "#DC2626", "Shallow": "#0F766E", "Intermediate": "#8B5CF6",
         "Deep": "#2563EB", "Northern": "#0EA5E9", "Southern": "#EC4899"}


def _color(label: str) -> str:
    return next((value for prefix,value in COLOR.items() if str(label).startswith(prefix)), "#94A3B8")


def create_sankey_diagram(data: pd.DataFrame) -> go.Figure:
    """Build magnitude band → depth category → hemisphere count-flow Sankey."""
    missing = set(CATEGORIES).difference(data.columns)
    if missing:
        raise ValueError(f"Sankey requires: {sorted(missing)}")
    valid = data.dropna(subset=list(CATEGORIES)).copy()
    fig = go.Figure()
    if valid.empty:
        fig.add_annotation(text="No earthquake records match these filters.", x=0.5, y=0.5,
                           xref="paper", yref="paper", showarrow=False)
        fig.update_layout(height=490)
        return fig

    first = valid.groupby([CATEGORIES[0], CATEGORIES[1]], observed=True).size().reset_index(name="value")
    second = valid.groupby([CATEGORIES[1], CATEGORIES[2]], observed=True).size().reset_index(name="value")
    # Namespaced node IDs avoid conflating equal labels in different stages.
    node_ids = []
    names = []
    for stage, field in enumerate(CATEGORIES):
        for label in sorted(valid[field].astype(str).unique()):
            node_ids.append((stage, label))
            names.append(label)
    lookup = {key: idx for idx, key in enumerate(node_ids)}
    sources, targets, values, colors = [], [], [], []
    for stage, table in [(0, first), (1, second)]:
        left, right = CATEGORIES[stage], CATEGORIES[stage + 1]
        for _, item in table.iterrows():
            source_label = str(item[left])
            sources.append(lookup[(stage, source_label)])
            targets.append(lookup[(stage + 1, str(item[right]))])
            values.append(int(item["value"]))
            colors.append("rgba(15,118,110,0.20)" if stage == 0 else "rgba(99,102,241,0.20)")

    fig.add_trace(go.Sankey(
        node=dict(label=names, color=[_color(label) for label in names],
                  pad=19, thickness=18, line=dict(color="#FFFFFF", width=1.2),
                  hovertemplate="<b>%{label}</b><br>Recorded events: %{value:,}<extra></extra>"),
        link=dict(source=sources, target=targets, value=values, color=colors,
                  hovertemplate="%{source.label} → %{target.label}<br>Count: %{value:,}<extra></extra>")
    ))
    fig.update_layout(height=500, margin=dict(l=12, r=12, t=48, b=12),
                      title="Magnitude band → Depth category → Hemisphere",
                      font=dict(size=12))
    return fig
