"""SEISMOSCOPE — Seismic Intelligence v4 / six-view research dashboard.
(3 MEMBERS CONTRİBUTED)
Run from the SEISMOSCOPE project root:
    python -m streamlit run app_seismic_v4.py

The nine graded visualizations come directly from the three tested member
packages in charts/. The ML section uses real saved training artifacts in ml/.
No synthetic earthquake data or substitute charts are created here.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from charts.geographic.geographic_categorical import (
    create_geographic_map,
    create_sankey_diagram,
    create_sunburst,
)
from charts.multidimensional.multidimensional import (
    complete_measurements,
    create_parallel_coordinates,
    create_scatter_3d,
    create_treemap,
    prepare_3d_data,
    summarize_locations,
)
from charts.statistical.statistical_temporal import (
    create_calendar_heatmap,
    create_density_contour_binned,
    create_density_contour_smoothed,
    create_violin_plot,
)
from ml.features import classification_features, clustering_features
from ml.ml_dashboard import render_ml_section


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "earthquakes_dashboard_ready.csv"
REFERENCE_PATH = ROOT / "data" / "kahramanmaras_6feb_major_events_reference.csv"
MODELS_DIR = ROOT / "ml" / "models"
REPORTS_DIR = ROOT / "ml" / "reports"
TEAL = "#0F766E"
SLATE = "#0F172A"

st.set_page_config(
    page_title="SEISMOSCOPE | Earthquake Data Explorer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* SEISMOSCOPE v4 — Seismic Intelligence visual identity */
    :root { --navy:#0F172A; --navy2:#172B4D; --teal:#0F766E;
            --indigo:#6366F1; --amber:#F59E0B; --slate:#64748B;
            --bg:#F8FAFC; --line:#DFE7EF; }
    .stApp { background:var(--bg); color:var(--navy); font-family:'Segoe UI',Arial,sans-serif; }
    [data-testid="stMainBlockContainer"], .block-container {
        max-width:1640px; padding-top:1.15rem; padding-bottom:2.3rem; }
    h1,h2,h3 { letter-spacing:-.025em; color:var(--navy); }
    [data-testid="stSidebar"] { background:#EDF3F7; border-right:1px solid #DCE5EC; }
    [data-testid="stSidebar"] .block-container { padding-top:1.4rem; }
    [data-testid="stSidebar"] label { font-weight:600; color:#334155; }
    .ss-brand-shell { background:linear-gradient(135deg,#0F172A,#203B59);
        margin:0 0 1.15rem; padding:17px 16px; border-radius:13px;
        border-bottom:3px solid #0D9488; box-shadow:0 8px 18px rgba(15,23,42,.08); }
    .ss-brand-name { color:#FFFFFF; font-weight:850; letter-spacing:.095em;
        font-size:1.14rem; line-height:1.1; }
    .ss-brand-kicker { color:#99F6E4; font-weight:700; letter-spacing:.14em;
        font-size:.63rem; margin-bottom:.5rem; }
    .ss-brand-sub { color:#CBD5E1; margin-top:.5rem; font-size:.7rem; }
    .ss-hero { position:relative; overflow:hidden; border-radius:17px;
        background:linear-gradient(112deg,#0F172A 8%,#172B4D 58%,#1B4A56 100%);
        min-height:184px; padding:28px 34px; color:white;
        display:flex; gap:2rem; align-items:center; justify-content:space-between;
        box-shadow:0 10px 30px rgba(15,23,42,.12); margin:0 0 1.0rem; }
    .ss-hero:after { content:''; position:absolute; width:350px; height:350px;
        border:1px solid rgba(94,234,212,.12); border-radius:50%; right:14%; top:-235px;
        box-shadow:0 0 0 44px rgba(94,234,212,.025),0 0 0 90px rgba(94,234,212,.018);
        pointer-events:none; }
    .ss-hero:before { content:''; position:absolute; width:180px; height:180px;
        border-radius:50%; border:1px solid rgba(94,234,212,.1);
        right:28%; bottom:-158px; pointer-events:none; }
    .ss-hero-body,.ss-hero-window { position:relative; z-index:1; }
    .ss-eyebrow { color:#5EEAD4; font-size:.72rem; letter-spacing:.14em;
        font-weight:800; text-transform:uppercase; margin-bottom:.65rem; }
    .ss-hero-title { font-size:clamp(2.1rem,3.2vw,3rem); font-weight:850;
        letter-spacing:-.055em; color:#FFFFFF; line-height:1.08; margin:0 0 .6rem; }
    .ss-hero-sub { font-size:.91rem; color:#D5E6EC; margin:0; }
    .ss-hero-window { border:1px solid rgba(255,255,255,.17);
        background:rgba(255,255,255,.09); backdrop-filter:blur(6px);
        padding:1rem 1.12rem; border-radius:11px; min-width:240px; }
    .ss-window-label { color:#9FF3E6; font-size:.63rem; letter-spacing:.09em; font-weight:800; }
    .ss-window-value { color:#FFFFFF; font-size:.92rem; font-weight:750; margin-top:.35rem; }
    [data-testid="stMetric"] { background:#FFFFFF; border:1px solid var(--line);
        border-radius:12px; padding:15px 20px; border-top:3px solid #0D9488;
        box-shadow:0 4px 20px rgba(15,23,42,.03); }
    [data-testid="stMetricLabel"] { color:#475569; font-size:.8rem; }
    [data-testid="stMetricValue"] { color:var(--navy); font-weight:750; }
    /* Native navigation is interactive; tabs are never replaced by inert HTML. */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        background:var(--navy2); padding:8px 9px; border-radius:12px;
        border:1px solid #203B59; gap:4px; margin-top:.6rem;
        box-shadow:0 7px 15px rgba(15,23,42,.09); }
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        color:#D8E6F0; background:transparent; border-radius:8px;
        font-size:.85rem; padding:.65rem .83rem; font-weight:600; }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        background:rgba(255,255,255,.10); color:#FFFFFF; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        background:#0F766E; color:#FFFFFF; font-weight:760; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background:#5EEAD4; }
    /* Nested tabs (Density Contour) remain light, separate from top navigation. */
    div[data-testid="stTabs"] div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        background:#F1F5F9; border:1px solid #DCE5EC; box-shadow:none; }
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"] {
        color:#334155; background:transparent; }
    div[data-testid="stTabs"] div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        color:#0F766E; background:#E4F5F1; }
    .ss-section-heading { margin:1.35rem 0 .7rem; }
    .ss-section-eyebrow { text-transform:uppercase; letter-spacing:.15em;
        color:#0F766E; font-size:.68rem; font-weight:850; }
    .ss-section-title { color:var(--navy); font-size:1.42rem;
        font-weight:820; letter-spacing:-.035em; margin:.27rem 0 .25rem; }
    .ss-section-desc { color:#526477; font-size:.88rem; margin:0; }
    .ss-card { background:#FFFFFF; border:1px solid var(--line);
        border-radius:12px; padding:18px 19px 18px; min-height:144px;
        border-top:3px solid #0F766E; box-shadow:0 4px 12px rgba(15,23,42,.025); }
    .ss-research-card { min-height: 194px; }
    .ss-card-accent { color:#0F766E; letter-spacing:.1em; text-transform:uppercase;
        font-size:.66rem; font-weight:850; }
    .ss-card-title { margin:.6rem 0 .35rem; color:var(--navy);
        font-size:1.02rem; font-weight:780; }
    .ss-card-text { color:#526477; font-size:.83rem; line-height:1.55; margin:0; }
    .ss-event-strip { background:#FFFFFF; border:1px solid var(--line);
        border-left:4px solid #F59E0B; border-radius:11px; padding:14px 16px;
        margin:.4rem 0; }
    .ss-event-title { color:#0F172A; font-weight:770; font-size:.93rem; }
    .ss-event-desc { color:#64748B; font-size:.79rem; margin-top:.3rem; }
    .ss-method-note { background:#EFF7F6; border:1px solid #D5E9E6;
        border-radius:11px; padding:14px 18px; color:#334155;
        font-size:.85rem; line-height:1.6; margin:.6rem 0 1rem; }
    .science-box { background:#FFFFFF; border:1px solid var(--line);
        border-left:3px solid #0F766E; border-radius:11px; padding:16px;
        color:#334155; line-height:1.55; font-size:.9rem; }
    .science-box strong { color:#0F172A; }
    .ss-focus-row { display:flex; justify-content:space-between; align-items:center;
        gap:1rem; border-bottom:1px solid #DCE5EC; padding:.35rem 0 .85rem; }
    .ss-focus-left { color:#0F172A; font-weight:770; font-size:1.02rem; }
    .ss-focus-right { color:#64748B; font-size:.77rem; }
    .ss-mini-band { background:linear-gradient(90deg,#E9F8F4,#F7FAFC);
        padding:12px 15px; border-radius:10px; border-left:3px solid #0F766E;
        color:#334155; font-size:.84rem; }
    @media (max-width: 1080px) {
        .ss-hero { padding:23px; flex-direction:column; align-items:flex-start; gap:1rem; }
        .ss-hero-window { min-width:0; width:100%; }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] { overflow-x:auto; flex-wrap:nowrap; }
        div[data-testid="stTabs"] button[data-baseweb="tab"] { white-space:nowrap; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner="Reading the reviewed earthquake catalog...")
def load_catalog() -> pd.DataFrame:
    """Load the reviewed catalog only. Fail rather than manufacture fallback data."""
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Required earthquake dataset not found: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH, parse_dates=["event_date_utc"], low_memory=False)
    required = {
        "id", "time", "event_date_utc", "latitude", "longitude", "mag",
        "depth", "magType", "magError", "latitude_hemisphere",
        "depth_exactly_10km", "magnitude_band", "depth_category", "place",
    }
    absent = sorted(required - set(data.columns))
    if absent:
        raise ValueError(f"The dataset is missing required columns: {absent}")
    if not 2000 <= len(data) <= 10000 or data.shape[1] < 7:
        raise ValueError(f"Unexpected catalog dimensions: {data.shape}")
    if data["id"].isna().any() or not data["id"].is_unique:
        raise ValueError("Earthquake event IDs must be unique and non-null.")
    if data["event_date_utc"].isna().any():
        raise ValueError("Invalid UTC dates found in the dataset.")
    return data


def filter_catalog(
    original: pd.DataFrame,
    mag_range: tuple[float, float],
    date_range: tuple[date, date] | list[date] | None,
    include_ten: bool,
    hemispheres: list[str],
) -> pd.DataFrame:
    """Apply exactly the same common filters to all nine primary charts."""
    result = original.loc[original["mag"].between(*mag_range)].copy()
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        return result.iloc[0:0].copy()  # Incomplete date choice is not full data.
    first, last = date_range
    if first > last:
        return result.iloc[0:0].copy()
    result = result.loc[result["event_date_utc"].dt.date.between(first, last)].copy()
    result = result.loc[result["latitude_hemisphere"].isin(hemispheres)].copy()
    if not include_ten:
        assigned = result["depth_exactly_10km"].astype(str).str.lower().eq("true")
        result = result.loc[~assigned].copy()
    return result


def explain(reading: str, caution: str) -> None:
    st.markdown(
        f'<div class="science-box"><strong>How to read</strong><p>{reading}</p>'
        f'<strong>Scientific note</strong><p>{caution}</p></div>',
        unsafe_allow_html=True,
    )


def plot_with_note(fig: go.Figure, key: str, reading: str, caution: str) -> None:
    left, right = st.columns([3.5, 1.2], gap="large")
    with left:
        with st.container(border=True):
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=SLATE))
            st.plotly_chart(fig, width="stretch",
                            config={"displaylogo": False}, key=key)
    with right:
        explain(reading, caution)


def choose_chart(title: str, options: list[str], *, key: str) -> str:
    if hasattr(st, "segmented_control"):
        value = st.segmented_control(title, options=options, default=options[0], key=key)
    else:
        value = st.radio(title, options, horizontal=True, key=key)
    return value or options[0]


def show_overview(filtered: pd.DataFrame, all_data: pd.DataFrame) -> None:
    """New landing page. All charts here summarize the reviewed CSV, never fake data."""
    st.markdown(
        '<div class="ss-section-heading">'
        '<div class="ss-section-eyebrow">01 / Mission control</div>'
        '<div class="ss-section-title">A clearer view of seismic activity</div>'
        '<p class="ss-section-desc">Explore a historical M4.5+ earthquake catalog, '
        'inspect nine visualizations, and review trained exploratory models.</p>'
        '</div>', unsafe_allow_html=True,
    )

    a, b = st.columns([1.75, 1], gap="large")
    with a:
        st.markdown("#### Monthly recorded earthquake activity")
        if filtered.empty:
            st.info("No earthquake records match the active filters. Change the filters to view monthly activity.")
        else:
            monthly = (filtered.groupby(filtered["event_date_utc"].dt.to_period("M"))
                       .size().rename("Records").reset_index())
            monthly["Month"] = monthly["event_date_utc"].dt.to_timestamp()
            fig = go.Figure(go.Scatter(
                x=monthly["Month"], y=monthly["Records"],
                mode="lines+markers", name="Recorded earthquakes",
                line=dict(color="#0F766E", width=3, shape="spline"),
                marker=dict(size=8, color="#0F766E", line=dict(color="#FFFFFF", width=1.5)),
                fill="tozeroy", fillcolor="rgba(15,118,110,0.09)",
                hovertemplate="%{x|%b %Y}<br><b>%{y:,} earthquakes</b><extra></extra>",
            ))
            fig.update_layout(
                height=340, margin=dict(l=8, r=14, t=10, b=32),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#475569"), showlegend=False,
                xaxis=dict(title=None, tickformat="%b %Y", showgrid=False),
                yaxis=dict(title="Recorded M4.5+ events", gridcolor="#E7EDF3", rangemode="tozero"),
            )
            with st.container(border=True):
                st.plotly_chart(fig, width="stretch", key="overview_monthly_activity",
                                config={"displaylogo": False})
            st.caption("Counts summarize recorded catalog events within the active dashboard filters; "
                       "they are not an estimate of all earthquake occurrence.")
    with b:
        st.markdown("#### Catalog at a glance")
        first = all_data["event_date_utc"].min().date()
        last = all_data["event_date_utc"].max().date()
        st.markdown(
            '<div class="ss-card">'
            '<div class="ss-card-accent">Source & coverage</div>'
            '<div class="ss-card-title">USGS ANSS ComCat</div>'
            f'<p class="ss-card-text">{first:%d %b %Y} – {last:%d %b %Y} (UTC)<br>'
            f'{len(all_data):,} catalogued M4.5+ records.<br>'
            'Geography: global. Measurements: catalog-reported.</p>'
            '</div>', unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ss-method-note"><strong>About the filters:</strong> '
            'The charts and the monthly activity summary use the sidebar selection. '
            'The dedicated 6 February page has a separate regional date range to preserve its context.</div>', unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="ss-section-heading">'
        '<div class="ss-section-eyebrow">02 / Geographic footprint</div>'
        '<div class="ss-section-title">Recorded epicenters across the globe</div>'
        '<p class="ss-section-desc">An at-a-glance location summary of your filtered catalog. '
        'For the full interactive map, visit Geographic &amp; Categorical.</p>'
        '</div>', unsafe_allow_html=True,
    )
    if filtered.empty:
        st.info("No mapped events match the active filters.")
    else:
        locations = filtered.dropna(subset=["latitude", "longitude", "mag"])
        if locations.empty:
            st.info("The filtered records have no valid geographic coordinates.")
        else:
            # Secondary overview map, not a replacement for Member 1's graded map.
            geo_fig = go.Figure(go.Scattergeo(
                lat=locations["latitude"], lon=locations["longitude"],
                mode="markers",
                customdata=locations[["id", "depth"]].to_numpy(),
                marker=dict(size=3.6, opacity=.62, color=locations["mag"],
                            colorscale=[[0,"#0F766E"],[.6,"#6366F1"],[1,"#F59E0B"]],
                            cmin=4.5, cmax=max(7.8,float(locations["mag"].max())),
                            colorbar=dict(title="Magnitude", thickness=12, len=.7)),
                hovertemplate="Event: %{customdata[0]}<br>Lat: %{lat:.2f}°<br>"
                              "Lon: %{lon:.2f}°<br>Depth: %{customdata[1]:.1f} km<extra></extra>",
            ))
            geo_fig.update_geos(
                projection_type="natural earth", showland=True, landcolor="#EAF0F5",
                showocean=True, oceancolor="#F8FBFD", showcoastlines=True,
                coastlinecolor="#B9C7D6", showcountries=True,
                countrycolor="#D0D9E3", showframe=False, bgcolor="rgba(0,0,0,0)",
            )
            geo_fig.update_layout(
                height=330, margin=dict(l=0,r=0,t=8,b=2),
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#475569"),
                showlegend=False,
            )
            with st.container(border=True):
                st.plotly_chart(geo_fig, width="stretch",
                                key="overview_global_snapshot", config={"displaylogo":False})
            st.caption(f"{len(locations):,} catalogued events with valid coordinates in the active selection. "
                       "Symbols are location markers, not shaking-area estimates.")

    st.markdown(
        '<div class="ss-section-heading">'
        '<div class="ss-section-eyebrow">03 / Research modules</div>'
        '<div class="ss-section-title">Follow the evidence across six views</div>'
        '</div>', unsafe_allow_html=True,
    )
    cards = [
        ("MEMBER 1", "Geographic & Categorical", "Map, Sankey, Sunburst · geographic and hierarchical distributions."),
        ("MEMBER 3", "Statistical & Temporal", "Density Contour, Violin, Calendar Heatmap · patterns in time and measurement quality."),
        ("MEMBER 2", "Multidimensional & 3D", "Treemap, Parallel Coordinates, 3D Scatter · higher-dimensional exploration."),
    ]
    cols = st.columns(3, gap="medium")
    for col, (eyebrow, title, description) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="ss-card ss-research-card"><div class="ss-card-accent">{eyebrow}</div>'
                f'<div class="ss-card-title">{title}</div>'
                f'<p class="ss-card-text">{description}</p></div>',
                unsafe_allow_html=True,
            )
    cols = st.columns(2, gap="medium")
    extra = [
        ("MODEL ANALYSIS", "Machine Learning", "Saved K-Means and Decision Tree models, held-out metrics and historical-event inference."),
        ("HISTORICAL FOCUS", "Türkiye · 6 February 2023", "Principal events, regional catalog and an idealized P/S-wave demonstration."),
    ]
    for col, (eyebrow, title, description) in zip(cols, extra):
        with col:
            st.markdown(
                f'<div class="ss-card ss-research-card"><div class="ss-card-accent">{eyebrow}</div>'
                f'<div class="ss-card-title">{title}</div>'
                f'<p class="ss-card-text">{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="ss-section-heading">'
        '<div class="ss-section-eyebrow">04 / Historical spotlight</div>'
        '<div class="ss-section-title">6 February 2023 · Kahramanmaraş sequence</div>'
        '<p class="ss-section-desc">Documented principal events in the reviewed historical references.</p>'
        '</div>', unsafe_allow_html=True,
    )
    if not REFERENCE_PATH.is_file():
        st.error(f"Required event reference CSV is missing: {REFERENCE_PATH}")
    else:
        refs = pd.read_csv(REFERENCE_PATH)
        needed = {"id", "time", "mag", "place"}
        if not needed.issubset(refs.columns):
            st.error("The 6 February event reference CSV is missing required columns.")
        else:
            focus = refs.loc[refs["id"].astype(str).isin(["us6000jllz", "us6000jlqa"])].copy()
            if len(focus) != 2:
                st.error("Both principal 6 February events were not found in the reference CSV.")
            else:
                cols = st.columns(2, gap="medium")
                for col, (_, item) in zip(cols, focus.sort_values("time").iterrows()):
                    with col:
                        st.markdown(
                            '<div class="ss-event-strip">'
                            f'<div class="ss-event-title">M {float(item["mag"]):.1f} · '
                            f'{"Pazarcık" if item["id"] == "us6000jllz" else "Elbistan"}</div>'
                            f'<div class="ss-event-desc">6 Feb 2023 · {str(item["time"])[11:16]} UTC · '
                            f'USGS ID: {item["id"]}</div>'
                            '</div>', unsafe_allow_html=True,
                        )
    st.markdown(
        '<div class="ss-method-note"><strong>Scientific scope:</strong> '
        'Historical recorded M4.5+ events are not a complete earthquake inventory. '
        'Catalog depths may include assigned values; cluster membership is not a hazard zone. '
        'Neither these visualizations nor the idealized wave simulation forecast earthquakes, '
        'shaking intensity or damage.</div>', unsafe_allow_html=True,
    )


def show_geographic(data: pd.DataFrame) -> None:
    st.subheader("Geographic & Categorical Analysis · Member 1")
    choice = choose_chart("Visualization", ["Geographic Map", "Sankey Diagram", "Sunburst"], key="m1_chart")
    if choice == "Geographic Map":
        mode = st.radio("Map mode", ["2D Map", "Orthographic Globe", "Monthly Animation"],
                        horizontal=True, key="m1_map_mode")
        plot_with_note(
            create_geographic_map(data, mode), "m1_map",
            "Each dot is a catalogued epicenter. Magnitude controls size and color. "
            "The animation is grouped by UTC month.",
            "Marker size does not represent actual shaking area. This catalog includes "
            "recorded M4.5+ events, not all earthquakes.",
        )
    elif choice == "Sankey Diagram":
        plot_with_note(
            create_sankey_diagram(data), "m1_sankey",
            "Read links from magnitude band to depth category and hemisphere. "
            "Their widths represent record counts.",
            "Links are descriptive category combinations, not physical migration or causation.",
        )
        if not data.empty:
            counts = data.groupby("magnitude_band", observed=True).size().reset_index(name="Records")
            st.dataframe(counts, width="stretch", hide_index=True)
    else:
        plot_with_note(
            create_sunburst(data), "m1_sunburst",
            "The concentric rings group hemisphere, magnitude band and depth category.",
            "The categories provide descriptive organization, not a physical earthquake model.",
        )
        if not data.empty:
            summary = data.groupby("latitude_hemisphere", observed=True).agg(
                Records=("id", "size"), Mean_magnitude=("mag", "mean")
            ).reset_index()
            st.dataframe(summary.round(2), width="stretch", hide_index=True)


def show_multidimensional(data: pd.DataFrame) -> None:
    st.subheader("Multidimensional & 3D Analysis · Member 2")
    choice = choose_chart("Visualization", ["Treemap", "Parallel Coordinates", "3D Scatter"], key="m2_chart")
    if choice == "Treemap":
        a, b = st.columns(2)
        top_n = a.slider("Top N locations", 5, 30, 15, 5, key="m2_top_n")
        palette = b.selectbox("Color palette", ["Member 2 final", "RdYlBu_r"], key="m2_palette")
        plot_with_note(
            create_treemap(data, top_n, palette), "m2_treemap",
            "Tile area is the count of recorded events sharing a USGS place label. "
            "Color shows mean magnitude.",
            "Place labels are descriptive strings, not standardized administrative regions.",
        )
        st.markdown("#### Top locations — statistical summary")
        summary = summarize_locations(data, top_n)
        if summary.empty:
            st.info("No locations match these filters.")
        else:
            st.dataframe(summary.round(2), width="stretch", hide_index=True)
    elif choice == "Parallel Coordinates":
        complete = complete_measurements(data)
        a, b, c = st.columns(3)
        a.metric("Selected records", f"{len(data):,}")
        b.metric("Complete measurements", f"{len(complete):,}")
        c.metric("Excluded for missingness", f"{len(data) - len(complete):,}")
        plot_with_note(
            create_parallel_coordinates(data), "m2_parallel",
            "Each polyline is one complete earthquake measurement. Brush any vertical "
            "axis to highlight subsets.",
            "Records missing any of the six measurements are omitted from this figure.",
        )
    else:
        a, b = st.columns(2)
        show_ten = a.checkbox("Show exact-10-km records in 3D", value=True, key="m2_show_10")
        marker = b.slider("Marker size", min_value=2, max_value=7, value=3, key="m2_marker")
        valid = prepare_3d_data(data, show_ten)
        st.caption(f"Displayed valid records: {len(valid):,}")
        plot_with_note(
            create_scatter_3d(data, show_ten, marker), "m2_scatter3d",
            "Rotate and zoom longitude, latitude and hypocentral depth. Magnitude is color.",
            "The depth axis is reversed. Some 10-km entries may be assigned catalog "
            "depths; removing them is a sensitivity check, not a correction.",
        )


def show_statistical(data: pd.DataFrame, all_data: pd.DataFrame,
                     selected_dates: tuple[date, date] | list[date] | None) -> None:
    st.subheader("Statistical & Temporal Analysis · Member 3")
    choice = choose_chart("Visualization", ["Density Contour", "Violin Plot", "Calendar Heatmap"], key="m3_chart")
    if choice == "Density Contour":
        view = st.selectbox("Chart range", ["Focused View", "Full Range"], key="m3_range")
        overview, detailed = st.tabs(["Overview Contours", "Detailed Bins"])
        with overview:
            plot_with_note(
                create_density_contour_smoothed(data, view), "m3_density_overview",
                "Automatically selected histogram bins reveal broad magnitude–depth concentration.",
                "This is a 2D histogram contour, not KDE. Some 10-km depths may be assigned.",
            )
        with detailed:
            plot_with_note(
                create_density_contour_binned(data, view), "m3_density_detailed",
                "Fine bins (0.05 magnitude × 10 km depth) reveal localized variation.",
                "Counts per bin depend on bin width; these two colorbars are not "
                "directly comparable.",
            )
    elif choice == "Violin Plot":
        # Preserve the three methods verified in the independent member project.
        methods = ["mb", "mww", "mwr"]
        selected = st.multiselect("Magnitude methods", methods, default=methods, key="m3_methods")
        valid = data.loc[data["magType"].isin(selected), ["magType", "magError"]].copy()
        valid["magError"] = pd.to_numeric(valid["magError"], errors="coerce")
        valid = valid.dropna(subset=["magError"])
        valid = valid.loc[valid["magError"] >= 0]
        a, b, c = st.columns(3)
        a.metric("Valid measurements", f"{len(valid):,}")
        b.metric("Methods selected", len(selected))
        c.metric("Median magnitude uncertainty",
                 f"{valid['magError'].median():.3f}" if not valid.empty else "—")
        plot_with_note(
            create_violin_plot(data, selected), "m3_violin",
            "Each violin shows the distribution of reported magnitude uncertainty. "
            "The inner box shows quartiles and median.",
            "Different measurement methods apply under different conditions. A smaller "
            "reported magError alone does not establish superior accuracy.",
        )
        st.markdown("#### Statistical summary")
        if valid.empty:
            st.info("No valid uncertainty measurements for these filters.")
        else:
            table = valid.groupby("magType")["magError"].agg(
                Records="size", Median="median", Mean="mean", Std_Dev="std"
            ).reindex(selected).round(3).reset_index().rename(columns={"magType": "Method"})
            st.dataframe(table, width="stretch", hide_index=True)
    else:
        years = sorted(all_data["event_date_utc"].dt.year.unique().astype(int).tolist())
        a, b = st.columns([1, 2])
        year = a.selectbox("Calendar year", years, key="m3_year")
        scope = b.selectbox("Geographic scope", ["Global", "6 Feb epicentral region (approximate)"],
                            key="m3_scope")
        calendar = data.copy()
        if scope != "Global":
            calendar = calendar.loc[calendar["latitude"].between(35, 40)
                                    & calendar["longitude"].between(34, 41)].copy()
        year_data = calendar.loc[calendar["event_date_utc"].dt.year.eq(year)].copy()
        daily = year_data.groupby("event_date_utc").size()
        a, b, c = st.columns(3)
        a.metric("Events in selected year", f"{len(year_data):,}")
        b.metric("Peak daily count", f"{int(daily.max()) if not daily.empty else 0:,}")
        if year == 2023:
            c.metric("6 Feb 2023 (UTC)", f"{int(daily.get(pd.Timestamp('2023-02-06'), 0)):,}")
        else:
            c.metric("Days with records", f"{len(daily):,}")
        min_day = all_data["event_date_utc"].min().date()
        max_day = all_data["event_date_utc"].max().date()
        start, end = ((selected_dates[0], selected_dates[1])
                      if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2
                      else (min_day, min_day))
        global_daily_max = int(all_data.groupby("event_date_utc").size().max())
        plot_with_note(
            create_calendar_heatmap(calendar, int(year), start, end,
                                    scale_max=global_daily_max), "m3_calendar",
            "Each square is one UTC day; hover for its catalogued event count. "
            "Amber highlights 6 February 2023.",
            "Color uses log(1 + count). The regional rectangle (35–40°N, 34–41°E) "
            "does not establish aftershock membership.",
        )
        st.markdown("#### Most active days")
        if daily.empty:
            st.info("No earthquake records match this year and selection.")
        else:
            top = daily.sort_values(ascending=False).head(5).rename_axis("UTC date").reset_index(name="Recorded events")
            st.dataframe(top, width="stretch", hide_index=True)


@st.cache_resource(show_spinner="Opening trained ML models...")
def load_saved_models():
    """Load trusted local artifacts created by python -m ml.train_models."""
    km_path = MODELS_DIR / "kmeans_pipeline.joblib"
    tree_path = MODELS_DIR / "decision_tree_classifier.joblib"
    if not km_path.is_file() or not tree_path.is_file():
        raise FileNotFoundError("Trained K-Means / Decision Tree .joblib files are missing.")
    return joblib.load(km_path), joblib.load(tree_path)


def show_ml(data: pd.DataFrame) -> None:
    needed = [REPORTS_DIR / "metrics.json", REPORTS_DIR / "ml_scored_events.csv",
              REPORTS_DIR / "cluster_profiles.csv"]
    missing = [str(p) for p in needed if not p.is_file()]
    if missing:
        st.error("Real ML reports are missing: " + ", ".join(missing))
        return
    try:
        cluster_model, tree_model = load_saved_models()
    except (FileNotFoundError, ValueError, ImportError) as exc:
        st.error(f"Could not load trained ML model artifacts: {exc}")
        return

    # Reported metrics are fixed held-out results; filters do not retrain models.
    render_ml_section(data)

    with st.expander("Verify live inference using saved trained models"):
        valid = data.dropna(subset=["id", "latitude", "longitude", "mag", "depth"])
        if valid.empty:
            st.info("No filtered historical events are available for model inference.")
            return
        event_ids = valid["id"].astype(str).tolist()
        default_id = "us6000jllz"
        initial = event_ids.index(default_id) if default_id in event_ids else 0
        chosen = st.selectbox("Historical USGS event ID", event_ids, index=initial,
                              key="ml_event_id")
        event = valid.loc[valid["id"].astype(str).eq(chosen)].iloc[[0]]
        predicted_group = int(cluster_model.predict(clustering_features(event))[0])
        predicted_depth = str(tree_model.predict(classification_features(event))[0])
        st.write(f"**K-Means cluster:** {predicted_group}")
        st.write(f"**Decision Tree predicted recorded-depth class:** {predicted_depth}")
        st.write(f"**Actual catalogued depth class:** {event.iloc[0]['depth_category']}")
        st.caption("This is inference on a known historical event. The classifier predicts "
                   "an existing depth category, not a future earthquake. K-Means was fitted "
                   "on the full historical catalog; the tree used a chronological train/test split.")


CITY_CENTERS = [
    ("Kahramanmaraş", 37.575, 36.922), ("Gaziantep", 37.066, 37.378),
    ("Osmaniye", 37.074, 36.246), ("Adıyaman", 37.764, 38.278),
    ("Kilis", 36.718, 37.121), ("Hatay (Antakya)", 36.202, 36.160),
    ("Malatya", 38.355, 38.309), ("Adana", 37.000, 35.321),
    ("Şanlıurfa", 37.159, 38.796), ("Mersin", 36.812, 34.641),
    ("Diyarbakır", 37.914, 40.230), ("Kayseri", 38.731, 35.478),
]


def haversine_km(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Surface great-circle distance between epicenter and city coordinates (km)."""
    radius = 6371.0
    a1 = np.radians(lat1)
    a2 = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(a1) * np.cos(a2) * np.sin(dlon / 2) ** 2
    return radius * 2 * np.arcsin(np.sqrt(a))


def wave_circle(lat: float, lon: float, km: float, points: int = 121) -> pd.DataFrame:
    """Spherical small-circle for a simplified idealized wavefront illustration."""
    theta = np.linspace(0, 2 * np.pi, points)
    angular = km / 6371.0
    phi = np.radians(lat)
    lam = np.radians(lon)
    p2 = np.arcsin(np.clip(np.sin(phi) * np.cos(angular)
                           + np.cos(phi) * np.sin(angular) * np.cos(theta), -1, 1))
    l2 = lam + np.arctan2(np.sin(theta) * np.sin(angular) * np.cos(phi),
                          np.cos(angular) - np.sin(phi) * np.sin(p2))
    return pd.DataFrame({"latitude": np.degrees(p2),
                         "longitude": ((np.degrees(l2) + 180) % 360) - 180})


def simulation_table(lat: float, lon: float, depth: float, t_seconds: int):
    p_speed, s_speed = 6.0, 3.5  # illustrative constant km/s velocities
    cities = pd.DataFrame(CITY_CENTERS, columns=["City", "latitude", "longitude"])
    epi = haversine_km(lat, lon, cities["latitude"].to_numpy(), cities["longitude"].to_numpy())
    hypo = np.sqrt(epi ** 2 + depth ** 2)
    cities["Epicentral distance (km)"] = np.round(epi, 1)
    cities["P arrival (s)"] = np.round(hypo / p_speed, 1)
    cities["S arrival (s)"] = np.round(hypo / s_speed, 1)
    cities["S minus P (s)"] = np.round(hypo / s_speed - hypo / p_speed, 1)
    cities["Status"] = np.select(
        [t_seconds >= hypo / s_speed, t_seconds >= hypo / p_speed],
        ["S wave arrived (model)", "P wave arrived (model)"],
        default="Neither arrived (model)",
    )
    return cities.sort_values("Epicentral distance (km)").reset_index(drop=True)


def show_wave_simulator(catalog: pd.DataFrame, refs: pd.DataFrame) -> None:
    st.markdown("---")
    st.subheader("Idealized P/S seismic-wave travel demonstration")
    st.caption("Educational constant-speed model: P ≈ 6.0 km/s and S ≈ 3.5 km/s. "
               "Not a measured wavefield, shaking intensity, damage footprint, or "
               "operational early-warning forecast.")

    # Two reference events come from the reviewed official event record file.
    options = refs.copy()
    optional_hatay = catalog.loc[catalog["id"].eq("us6000jqcn")]
    if not optional_hatay.empty:
        options = pd.concat([options, optional_hatay[refs.columns]], ignore_index=True)
    names = []
    for _, event in options.iterrows():
        event_date = str(event["time"])[:10]
        names.append(f"{event_date} · M{event['mag']:.1f} · {event['place']}")
    a, b = st.columns([2, 3])
    selection = a.selectbox("Recorded epicenter", list(range(len(options))),
                            format_func=lambda i: names[i], key="wave_event")
    seconds = b.slider("Seconds after origin time (idealized)", 5, 110, 40, 5,
                       key="wave_elapsed")
    record = options.iloc[selection]
    lat, lon, depth = (float(record[name]) for name in ("latitude", "longitude", "depth"))
    p_speed, s_speed = 6.0, 3.5
    p_radius = np.sqrt(max(0.0, (p_speed * seconds) ** 2 - depth ** 2))
    s_radius = np.sqrt(max(0.0, (s_speed * seconds) ** 2 - depth ** 2))
    result = simulation_table(lat, lon, depth, seconds)
    count_s = int(result["Status"].eq("S wave arrived (model)").sum())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("P-wave surface radius", f"{p_radius:,.1f} km")
    k2.metric("S-wave surface radius", f"{s_radius:,.1f} km")
    k3.metric("Illustrative S-front area", f"{np.pi * s_radius**2:,.0f} km²")
    k4.metric("City centers reached by S (model)", f"{count_s} / {len(result)}")

    rings = []
    for label, radius in [("P-wave front", p_radius), ("S-wave front", s_radius)]:
        ring = wave_circle(lat, lon, float(radius))
        ring["Wave"] = label
        rings.append(ring)
    ring_df = pd.concat(rings, ignore_index=True)
    line_fn = px.line_map if hasattr(px, "line_map") else px.line_mapbox
    scatter_fn = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
    fig = line_fn(ring_df, lat="latitude", lon="longitude", color="Wave",
                  color_discrete_map={"P-wave front": "#0284c7", "S-wave front": "#E11D48"},
                  center={"lat": lat, "lon": lon}, zoom=5.6, height=480)
    fig.update_traces(line=dict(width=3.5))
    colors = {
        "S wave arrived (model)": "#E11D48",
        "P wave arrived (model)": "#F59E0B",
        "Neither arrived (model)": "#10B981",
    }
    dot = scatter_fn(result, lat="latitude", lon="longitude", color="Status",
                     hover_name="City", color_discrete_map=colors,
                     hover_data={"Epicentral distance (km)": True,
                                 "P arrival (s)": True, "S arrival (s)": True,
                                 "latitude": False, "longitude": False})
    dot.update_traces(marker=dict(size=12))
    for trace in dot.data:
        fig.add_trace(trace)
    if hasattr(px, "line_map"):
        fig.update_layout(map_style="carto-positron")
    else:
        fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(title=f"Idealized travel fronts at t = {seconds} s",
                      margin=dict(l=0, r=0, t=50, b=0), legend=dict(orientation="h"))

    chart = px.bar(result.sort_values("Epicentral distance (km)", ascending=False),
                   y="City", x=["P arrival (s)", "S arrival (s)"], orientation="h",
                   barmode="group", height=480,
                   color_discrete_sequence=["#0284c7", "#E11D48"],
                   title="Idealized arrival time at selected city centers")
    chart.add_vline(x=seconds, line_dash="dash", line_color=TEAL,
                    annotation_text=f"Selected t = {seconds} s")
    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(fig, width="stretch", key="wave_map")
    with right:
        st.plotly_chart(chart, width="stretch", key="wave_arrivals")
    with st.expander("City-by-city distances and illustrative arrival times", expanded=True):
        st.dataframe(result.drop(columns=["latitude", "longitude"]),
                     width="stretch", hide_index=True)
    st.warning("This assumes constant wave speeds and straight-line hypocentral travel. "
               "Real seismic waves depend on geology, paths, phases and site effects. "
               "The S–P time difference is not a measured or guaranteed warning window. "
               "Neither arrival nor radius indicates how damaging shaking would be.")


def show_february_6(catalog: pd.DataFrame) -> None:
    """Sixth dashboard view: referenced events, regional context and wave demo.

    Keep the three explorations separate to avoid an excessively long page.
    This is an interface refactor only: the source records, regional selection,
    plots, and idealized P/S travel-time calculations are not changed.
    """
    st.markdown(
        '<div class="ss-section-heading">'
        '<div class="ss-section-eyebrow">06 / HISTORICAL FOCUS</div>'
        '<div class="ss-section-title">Türkiye · 6 February 2023</div>'
        '<p class="ss-section-desc">Documented major events, regional catalogue context and a '
        'simplified seismic-wave demonstration.</p>'
        '</div>', unsafe_allow_html=True,
    )
    st.caption("The regional sample is geographical, not a verified aftershock catalogue. "
               "The wave model is illustrative, not a forecast or damage estimate.")
    if not REFERENCE_PATH.is_file():
        st.error(f"Reference file for the two documented main events is missing: {REFERENCE_PATH}")
        return
    refs = pd.read_csv(REFERENCE_PATH)
    required = {"id", "time", "latitude", "longitude", "depth", "mag", "place"}
    if required - set(refs.columns) or len(refs) < 2:
        st.error("The 6 February reference CSV is incomplete.")
        return

    section = st.radio(
        "Explore Türkiye 2023",
        ["Historical Events", "Regional Analysis", "Wave Simulation"],
        horizontal=True, key="feb6_section",
    )

    if section == "Historical Events":
        st.markdown("#### Documented principal earthquakes")
        st.dataframe(
            refs[["time", "place", "mag", "depth", "latitude", "longitude", "id"]],
            hide_index=True, width="stretch",
        )
        a, b = st.columns(2)
        with a:
            st.markdown(
                '<div class="ss-event-strip">'
                '<div class="ss-event-title">M7.8 · Pazarcık</div>'
                '<div class="ss-event-desc">6 February 2023 · 01:17 UTC · '
                'USGS ID: us6000jllz</div></div>', unsafe_allow_html=True,
            )
        with b:
            st.markdown(
                '<div class="ss-event-strip">'
                '<div class="ss-event-title">M7.5 · Elbistan</div>'
                '<div class="ss-event-desc">6 February 2023 · 10:24 UTC · '
                'USGS ID: us6000jlqa</div></div>', unsafe_allow_html=True,
            )
        st.info("These are historical source records. This dashboard does not "
                "classify other nearby earthquakes as verified aftershocks.")
        return

    if section == "Wave Simulation":
        show_wave_simulator(catalog, refs)
        return

    # Regional Analysis: preserve original geographical rectangle and date logic.
    st.markdown("#### Regional seismicity · geographic sample")
    start = date(2023, 2, 1)
    finish = min(date(2023, 3, 6), catalog["event_date_utc"].max().date())
    date_window = st.date_input(
        "Regional UTC analysis window", (start, finish),
        min_value=catalog["event_date_utc"].min().date(),
        max_value=catalog["event_date_utc"].max().date(), key="feb6_window",
    )
    if not isinstance(date_window, (tuple, list)) or len(date_window) != 2:
        region = catalog.iloc[0:0].copy()
    else:
        region = catalog.loc[
            catalog["latitude"].between(35.5, 42.5)
            & catalog["longitude"].between(25.5, 45.0)
            & catalog["event_date_utc"].dt.date.between(*date_window)
        ].copy()
    a, b, c = st.columns(3)
    a.metric("Catalogued events in region/window", f"{len(region):,}")
    b.metric("Max reported magnitude", f"{region['mag'].max():.1f}" if not region.empty else "—")
    c.metric("Median depth", f"{region['depth'].median():.1f} km" if not region.empty else "—")
    if region.empty:
        st.info("No events match the selected regional window.")
    else:
        focus = st.radio(
            "Map focus",
            ["Earthquake region", "Pazarcık · M7.8", "Elbistan · M7.5", "Hatay / Antakya"],
            horizontal=True, key="feb6_focus",
        )
        centers = {
            "Earthquake region": (37.5, 37.0, 5.7),
            "Pazarcık · M7.8": (37.2256, 37.0143, 8.0),
            "Elbistan · M7.5": (38.0106, 37.1962, 8.0),
            "Hatay / Antakya": (36.1616, 36.0251, 8.0),
        }
        lat, lon, zoom = centers[focus]
        view = region.copy()
        view["point_size"] = (view["mag"].sub(4).clip(lower=0.25) ** 2.1)
        map_fn = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
        map_fig = map_fn(
            view, lat="latitude", lon="longitude", color="mag", size="point_size",
            size_max=18, hover_name="place",
            hover_data={"mag": ":.1f", "depth": ":.1f", "point_size": False},
            color_continuous_scale="YlOrRd", center={"lat": lat, "lon": lon},
            zoom=zoom, height=450, title="Catalogued regional epicenters",
        )
        if hasattr(px, "scatter_map"):
            map_fig.update_layout(map_style="carto-positron")
        else:
            map_fig.update_layout(mapbox_style="carto-positron")
        timeline = px.scatter(
            view.sort_values("event_date_utc"), x="event_date_utc", y="mag",
            color="depth", size="point_size", size_max=16, hover_name="place",
            color_continuous_scale="Plasma", height=450,
            title="Recorded magnitude versus UTC date",
        )
        left, right = st.columns([3, 2])
        with left:
            st.plotly_chart(map_fig, width="stretch", key="feb6_event_map")
        with right:
            st.plotly_chart(timeline, width="stretch", key="feb6_timeline")
        st.caption("The selected rectangle (35.5–42.5°N, 25.5–45°E) can include "
                   "earthquakes unrelated to the February 6 sequence.")


def main() -> None:
    try:
        all_data = load_catalog()
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"SEISMOSCOPE cannot load its reviewed dataset: {error}")
        st.stop()

    min_day = all_data["event_date_utc"].min().date()
    max_day = all_data["event_date_utc"].max().date()
    lower_mag = float(np.floor(all_data["mag"].min() * 10) / 10)
    upper_mag = float(np.ceil(all_data["mag"].max() * 10) / 10)

    with st.sidebar:
        st.markdown(
            '<div class="ss-brand-shell">'
            '<div class="ss-brand-kicker">GLOBAL SEISMIC INTELLIGENCE</div>'
            '<div class="ss-brand-name">◈ SEISMOSCOPE</div>'
            '<div class="ss-brand-sub">HISTORICAL CATALOG · FILTERS</div>'
            '</div>', unsafe_allow_html=True,
        )
        st.caption("USGS ANSS ComCat · global M4.5+ · UTC")
        mag = st.slider("Magnitude range", lower_mag, upper_mag,
                        value=(lower_mag, upper_mag), step=0.1, key="global_mag")
        days = st.date_input("UTC date range", (min_day, max_day),
                             min_value=min_day, max_value=max_day, key="global_days")
        ten = st.checkbox("Include depths recorded as exactly 10 km", True, key="global_ten")
        hemi = st.multiselect("Hemisphere", ["Northern", "Southern"],
                              default=["Northern", "Southern"], key="global_hemi")
        st.divider()
        st.caption("These common filters affect the nine primary visualizations and "
                   "the ML event view. The dedicated 6 February section uses its "
                   "own regional UTC window so the historical reference remains visible.")

    filtered = filter_catalog(all_data, mag, days, ten, hemi)
    st.markdown(
        '<div class="ss-hero">'
        '<div class="ss-hero-body"><div class="ss-eyebrow">GLOBAL SEISMIC INTELLIGENCE · HISTORICAL OBSERVATORY</div>'
        '<h1 class="ss-hero-title">SEISMOSCOPE</h1>'
        '<p class="ss-hero-sub">Earthquake Data Exploration &amp; Machine Learning'
        ' · Reviewed USGS Catalog</p></div>'
        '<div class="ss-hero-window"><div class="ss-window-label">OBSERVATION WINDOW · UTC</div>'
        f'<div class="ss-window-value">{min_day:%d %b %Y} – {max_day:%d %b %Y}</div></div>'
        '</div>', unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    a.metric("Earthquakes selected", f"{len(filtered):,}")
    b.metric("Maximum magnitude", f"{filtered['mag'].max():.1f}" if not filtered.empty else "—")
    c.metric("Median depth", f"{filtered['depth'].median():.1f} km" if not filtered.empty else "—")

    overview_tab, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⌂ Overview", "◎ Geographic", "▥ Statistical & Temporal",
        "◈ Multidimensional & 3D", "◇ Machine Learning", "◉ Türkiye · Feb 2023",
    ])
    with overview_tab:
        show_overview(filtered, all_data)
    with tab1:
        show_geographic(filtered)
    with tab2:
        show_statistical(filtered, all_data, days)
    with tab3:
        show_multidimensional(filtered)
    with tab4:
        show_ml(filtered)
    with tab5:
        show_february_6(all_data)
    st.divider()
    st.caption(f"Source: reviewed USGS ANSS ComCat historical catalog · "
               f"{len(all_data):,} M4.5+ events · all dates UTC. "
               "Charts summarize observations, not future earthquake predictions or hazard forecasts.")


if __name__ == "__main__":
    main()
