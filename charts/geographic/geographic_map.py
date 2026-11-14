"""Member 1 — worldwide earthquake location maps.

Based on the team's combined app.py geographic-map implementation. Graph
functions accept a filtered pandas DataFrame; they do not read CSV files.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_geographic_map(data: pd.DataFrame, mode: str = "2D Map") -> go.Figure:
    """Build an interactive 2D map, orthographic globe, or monthly animation."""
    required = {"latitude", "longitude", "mag", "depth"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Geographic Map requires: {sorted(missing)}")
    if mode not in ("2D Map", "Orthographic Globe", "Monthly Animation"):
        raise ValueError("mode must be 2D Map, Orthographic Globe or Monthly Animation")

    plot = data.dropna(subset=["latitude", "longitude", "mag", "depth"]).copy()
    plot["size_mag"] = (plot["mag"].sub(4.2).clip(lower=0.25) ** 2.15).round(2)
    hover = {"mag": ":.1f", "depth": ":.1f", "latitude": ":.2f", "longitude": ":.2f", "size_mag": False}
    if "event_date_utc" in plot.columns:
        plot["date_str"] = pd.to_datetime(plot["event_date_utc"], errors="coerce").dt.strftime("%Y-%m-%d")
        hover["date_str"] = True
    place = "place" if "place" in plot.columns else None
    titles = {"mag": "Magnitude (M)", "depth": "Hypocentral depth (km)", "date_str": "UTC date"}
    scale = "YlOrRd"

    if plot.empty:
        fig = go.Figure()
        fig.add_annotation(text="No earthquake records match these filters.", x=0.5, y=0.5,
                           xref="paper", yref="paper", showarrow=False)
        fig.update_layout(height=540)
        return fig

    if mode == "Orthographic Globe":
        fig = px.scatter_geo(plot, lat="latitude", lon="longitude", color="mag",
                             size="size_mag", size_max=18, opacity=0.82,
                             projection="orthographic", color_continuous_scale=scale,
                             hover_name=place, hover_data=hover, labels=titles, height=540)
        fig.update_geos(showland=True, landcolor="#F1F5F9", showocean=True,
                        oceancolor="#E0F2FE", showcountries=True,
                        countrycolor="#CBD5E1", coastlinecolor="#94A3B8",
                        showcoastlines=True, bgcolor="rgba(0,0,0,0)")
    else:
        plot_fn = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
        kwargs = dict(lat="latitude", lon="longitude", color="mag", size="size_mag",
                      size_max=18, hover_name=place, hover_data=hover,
                      labels=titles, zoom=1.3, height=540,
                      color_continuous_scale=scale)
        if mode == "Monthly Animation":
            if "time" in plot.columns:
                moment = pd.to_datetime(plot["time"], errors="coerce", utc=True)
            elif "event_date_utc" in plot.columns:
                moment = pd.to_datetime(plot["event_date_utc"], errors="coerce", utc=True)
            else:
                raise ValueError("Monthly Animation requires time or event_date_utc")
            plot["year_month"] = moment.dt.strftime("%Y-%m")
            plot = plot.dropna(subset=["year_month"]).sort_values("year_month")
            if plot.empty:
                fig = go.Figure()
                fig.add_annotation(text="No valid UTC dates to animate.",x=0.5,y=0.5,xref="paper",yref="paper",showarrow=False)
                return fig
            kwargs["animation_frame"] = "year_month"
            # Shared color range prevents magnitude coloring from changing each month.
            kwargs["range_color"] = (4.5, 7.8)
        fig = plot_fn(plot, **kwargs)
        if hasattr(px, "scatter_map"):
            fig.update_layout(map_style="carto-positron")
        else:
            fig.update_layout(mapbox_style="carto-positron")
        fig.update_traces(marker=dict(opacity=0.8))

    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), height=550,
                      title="Recorded M4.5+ earthquake locations — " + mode,
                      coloraxis_colorbar=dict(title="Magnitude"))
    return fig
