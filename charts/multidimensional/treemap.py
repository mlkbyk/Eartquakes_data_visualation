"""Member 2 — location Treemap from dataviz.txt final version.

The original Colab implementation used the most common 15 place strings and
colored boxes by their mean recorded magnitude. A Top-N control is added here.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

FINAL_COLORS = ["#24476B", "#4C789A", "#F4C66A", "#E87555"]


def summarize_locations(data: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    required = {"place", "mag", "id"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Treemap requires: {sorted(missing)}")
    valid = data.dropna(subset=["place", "mag", "id"])
    summary = (valid.groupby("place", observed=True)
               .agg(earthquake_count=("id", "count"), avg_magnitude=("mag", "mean"))
               .reset_index().sort_values("earthquake_count", ascending=False))
    return summary.head(top_n)


def create_treemap(data: pd.DataFrame, top_n: int = 15, palette: str = "Member 2 final") -> go.Figure:
    """Area = event count; color = mean magnitude of the location label."""
    summary = summarize_locations(data, top_n=top_n)
    if palette not in ("Member 2 final", "RdYlBu_r"):
        raise ValueError("Unknown palette")
    if summary.empty:
        fig = go.Figure()
        fig.add_annotation(text="No valid location records match these filters.",x=0.5,y=0.5,
                           xref="paper",yref="paper",showarrow=False)
        return fig
    fig = px.treemap(summary, path=["place"], values="earthquake_count",
                     color="avg_magnitude",
                     color_continuous_scale=FINAL_COLORS if palette == "Member 2 final" else "RdYlBu_r",
                     hover_data={"earthquake_count": True, "avg_magnitude": ":.2f"},
                     title=f"Global earthquake records by location — Top {len(summary)}", height=580)
    fig.update_traces(textinfo="label+value", marker=dict(line=dict(color="white", width=2)),
        hovertemplate="<b>%{label}</b><br>Earthquake count: %{value:,}<br>Average magnitude: %{color:.2f} M<extra></extra>")
    fig.update_layout(margin=dict(l=12,r=12,t=56,b=12),title_x=0.5)
    return fig
