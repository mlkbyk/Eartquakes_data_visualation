import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLUMNS = ["latitude", "longitude", "depth", "mag", "place"]


def prepare_3d_data(data: pd.DataFrame, include_exact_10km: bool = True) -> pd.DataFrame:
    missing = set(COLUMNS).difference(data.columns)
    if missing:
        raise ValueError(f"3D Scatter requires: {sorted(missing)}")
    clean = data[COLUMNS].dropna().copy()
    if not include_exact_10km:
        clean = clean.loc[~clean["depth"].eq(10.0)].copy()
    return clean


def create_scatter_3d(data: pd.DataFrame, include_exact_10km: bool = True, marker_size: int = 3) -> go.Figure:
    """Plot longitude × latitude × hypocentral depth, magnitude as color."""
    clean = prepare_3d_data(data, include_exact_10km)
    if clean.empty:
        fig = go.Figure()
        fig.add_annotation(text="No valid earthquake records match these filters.",x=0.5,y=0.5,
                           xref="paper",yref="paper",showarrow=False)
        return fig
    fig = px.scatter_3d(clean, x="longitude", y="latitude", z="depth", color="mag",
                        hover_name="place", hover_data=["latitude", "longitude", "depth", "mag"],
                        color_continuous_scale="RdYlBu_r",
                        title="3D global earthquake distribution", height=660)
    fig.update_traces(marker=dict(size=marker_size, opacity=0.75))
    fig.update_layout(margin=dict(l=8,r=8,t=50,b=8),
                      scene=dict(xaxis_title="Longitude (°)",
                                 yaxis_title="Latitude (°)",
                                 zaxis_title="Depth (km)",
                                 zaxis=dict(autorange="reversed")))
    return fig
