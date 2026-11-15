"""Member 2 — 6-axis Parallel Coordinates from original dataviz.txt notebook.""" 
import pandas as pd
import plotly.graph_objects as go

PARAMETERS = ["mag", "depth", "rms", "gap", "nst", "magError"]
AXIS_NAMES = ["Magnitude (M)", "Depth (km)", "RMS (s)",
              "Azimuthal gap (°)", "Number of stations", "Magnitude error"]
FINAL_SCALE = [[0, "#24476B"], [0.35, "#4C789A"],
               [0.65, "#F4C66A"], [1, "#E87555"]]


def complete_measurements(data: pd.DataFrame) -> pd.DataFrame:
    missing = set(PARAMETERS).difference(data.columns)
    if missing:
        raise ValueError(f"Parallel Coordinates requires: {sorted(missing)}")
    result = data[PARAMETERS].copy()
    for col in PARAMETERS:
        result[col] = pd.to_numeric(result[col], errors="coerce")
    return result.dropna()


def create_parallel_coordinates(data: pd.DataFrame) -> go.Figure:
    """Each polyline represents an earthquake with six nonmissing measurements."""
    full = complete_measurements(data)
    if full.empty:
        fig = go.Figure()
        fig.add_annotation(text="No records have all six required measurements.",x=0.5,y=0.5,
                           xref="paper",yref="paper",showarrow=False)
        return fig
    lo, hi = float(full.mag.min()), float(full.mag.max())
    if hi <= lo:
        hi = lo + 0.01
    fig = go.Figure(go.Parcoords(
        line=dict(color=full["mag"], colorscale=FINAL_SCALE,
                  cmin=lo,cmax=hi,showscale=True,colorbar=dict(title="Magnitude (M)")),
        dimensions=[dict(label=label, values=full[col])
                    for col,label in zip(PARAMETERS, AXIS_NAMES)]
    ))
    fig.update_layout(title="Multidimensional earthquake and measurement-quality analysis",
                      height=620, margin=dict(l=75,r=75,t=90,b=50))
    return fig
