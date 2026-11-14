
"""SEISMOSCOPE | Statistical and Temporal Analysis Preview."""

from pathlib import Path

import pandas as pd
import streamlit as st

from charts.statistical_temporal import (
    create_density_contour_smoothed,
    create_density_contour_binned,
    create_violin_plot,
    create_calendar_heatmap,
)

from charts.chart_style import apply_clean_chart_style
from ui.styles import apply_app_style


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SEISMOSCOPE | Statistical Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_app_style()


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:

    path = (
        Path(__file__).resolve().parent
        / "data"
        / "earthquakes_dashboard_ready.csv"
    )

    return pd.read_csv(
        path,
        parse_dates=["event_date_utc"]
    )


# --------------------------------------------------
# REUSABLE UI COMPONENTS
# --------------------------------------------------

def show_insight(
    main_text: str,
    note_text: str
) -> None:

    """Display a unified scientific information card."""

    st.markdown(
        '<div class="insight-card">'
        '<h4>How to read</h4>'
        f'<div>{main_text}</div>'
        f'<div class="insight-note">'
        f'<b>Scientific note</b><br>{note_text}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def show_density_chart(
    fig,
    description: str,
    chart_key: str,
    record_count: int
) -> None:

    """Show a density chart and its scientific explanation."""

    chart_col, note_col = st.columns(
        [3.5, 1.2],
        gap="large"
    )

    with chart_col:

        with st.container(
            border=True,
            key=f"chart_card_{chart_key}"
        ):

            st.plotly_chart(
                apply_clean_chart_style(fig),
                use_container_width=True,
                config={"displaylogo": False},
                key=chart_key
            )

    with note_col:

        show_insight(
            description,

            "Some depths of exactly 10 km may be "
            "assigned values. Compare the sidebar "
            "checkbox states before interpretation."
        )

    st.caption(
        f"{record_count:,} filtered earthquake records · "
        "Drag to zoom · Double-click to reset"
    )


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = load_data()

min_date = df["event_date_utc"].min().date()
max_date = df["event_date_utc"].max().date()


# --------------------------------------------------
# SIDEBAR — GLOBAL FILTERS
# --------------------------------------------------

with st.sidebar:

    st.subheader("Explore the data")

    st.caption("USGS earthquake records | M4.5+")

    st.divider()

    magnitude_range = st.slider(
        "Magnitude range",
        4.5,
        7.8,
        (4.5, 7.8),
        step=0.1
    )

    dates = st.date_input(
        "UTC date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    include_10km = st.checkbox(
        "Include depths recorded as exactly 10 km",
        value=True
    )

    st.caption(
        "Filters apply to the selected visualization."
    )


# --------------------------------------------------
# APPLY GLOBAL FILTERS
# --------------------------------------------------

filtered = df.loc[
    df["mag"].between(*magnitude_range)
].copy()

if isinstance(dates, (tuple, list)) and len(dates) == 2:

    filtered = filtered.loc[
        filtered["event_date_utc"].dt.date.between(
            *dates
        )
    ]

if not include_10km:

    ten_km = (
        filtered["depth_exactly_10km"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    filtered = filtered.loc[~ten_km]


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<span class="eyebrow-badge">'
    'GLOBAL EARTHQUAKE INTELLIGENCE'
    '</span>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-heading">'
    'SEISMOSCOPE'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-caption">'
    'Statistical &amp; Temporal Analysis · '
    'February 2023 – May 2024 · UTC'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# GLOBAL KPI METRICS
# --------------------------------------------------

k1, k2, k3 = st.columns(3)

k1.metric(
    "Earthquakes selected",
    f"{len(filtered):,}"
)

k2.metric(
    "Maximum magnitude",
    f"{filtered['mag'].max():.1f}"
    if not filtered.empty else "—"
)

k3.metric(
    "Median depth",
    f"{filtered['depth'].median():.1f} km"
    if not filtered.empty else "—"
)


# --------------------------------------------------
# VISUALIZATION NAVIGATOR
# --------------------------------------------------

st.markdown("#### Explore visualizations")


chart_choices = [
    "Density Contour",
    "Violin Plot",
    "Calendar Heatmap"
]

if hasattr(st, "segmented_control"):

    chosen_chart = st.segmented_control(
        "Choose visualization",
        options=chart_choices,
        default="Density Contour",
        key="visualization_navigator",
        label_visibility="collapsed"
    )

else:

    chosen_chart = st.radio(
        "Choose visualization",
        options=chart_choices,
        horizontal=True,
        key="visualization_navigator",
        label_visibility="collapsed"
    )


# --------------------------------------------------
# VISUALIZATION 1 — DENSITY CONTOUR
# --------------------------------------------------

if chosen_chart in (None, "Density Contour"):

    header_col, control_col = st.columns(
        [3, 1],
        gap="large"
    )

    with header_col:

        st.subheader(
            "Magnitude × Depth Density Contour"
        )

        st.caption(
            "Two complementary views of the same "
            "earthquakes, using different histogram "
            "bin widths."
        )

    with control_col:

        view = st.selectbox(
            "Chart range",
            ["Focused View", "Full Range"]
        )

    overview_tab, detailed_tab = st.tabs([
        "Overview Contours",
        "Detailed Bins"
    ])

    with overview_tab:

        show_density_chart(
            create_density_contour_smoothed(
                filtered,
                view
            ),

            "Automatically chosen bins show the broader "
            "magnitude–depth concentration pattern. "
            "This is a histogram contour, not a KDE estimate.",

            "density_overview",
            len(filtered)
        )

    with detailed_tab:

        show_density_chart(
            create_density_contour_binned(
                filtered,
                view
            ),

            "Fixed fine bins (0.05 magnitude × 10 km depth) "
            "reveal local concentrations. Colorbar counts "
            "cannot be directly compared to Overview counts.",

            "density_detailed",
            len(filtered)
        )


# --------------------------------------------------
# VISUALIZATION 2 — VIOLIN PLOT
# --------------------------------------------------

elif chosen_chart == "Violin Plot":

    st.subheader(
        "Magnitude Uncertainty by Estimation Method"
    )

    st.caption(
        "Compare reported magnitude uncertainty "
        "across earthquake magnitude estimation methods."
    )


    # ----------------------------------------------
    # METHOD SELECTION
    # ----------------------------------------------

    method_counts = (
        filtered.dropna(subset=["magError"])["magType"]
        .value_counts()
    )

    available_methods = (
        method_counts[method_counts >= 30]
        .index.tolist()
    )

    selected_methods = st.multiselect(
        "Magnitude estimation methods",
        options=available_methods,
        default=available_methods,
        help=(
            "Methods need at least 30 valid records "
            "after filtering."
        )
    )


    # ----------------------------------------------
    # FILTER VIOLIN DATA
    # ----------------------------------------------

    violin_data = filtered.loc[
        filtered["magType"].isin(selected_methods),
        ["magType", "magError"]
    ].copy()

    violin_data["magError"] = pd.to_numeric(
        violin_data["magError"],
        errors="coerce"
    )

    violin_data = violin_data.dropna(
        subset=["magError"]
    )

    violin_data = violin_data.loc[
        violin_data["magError"] >= 0
    ]


    # ----------------------------------------------
    # VIOLIN KPI METRICS
    # ----------------------------------------------

    v1, v2, v3 = st.columns(3)

    v1.metric(
        "Valid measurements",
        f"{len(violin_data):,}"
    )

    v2.metric(
        "Methods selected",
        len(selected_methods)
    )

    v3.metric(
        "Median uncertainty",
        f"{violin_data['magError'].median():.3f}"
        if not violin_data.empty else "—"
    )


    # ----------------------------------------------
    # VIOLIN CHART
    # ----------------------------------------------

    chart_col, note_col = st.columns(
        [3.5, 1.2],
        gap="large"
    )

    with chart_col:

        with st.container(
            border=True,
            key="chart_card_violin"
        ):

            st.plotly_chart(
                apply_clean_chart_style(
                    create_violin_plot(
                        filtered,
                        selected_methods
                    )
                ),
                use_container_width=True,
                config={"displaylogo": False},
                key="magnitude_violin_plot"
            )

    with note_col:

        show_insight(
            "Each violin represents uncertainty values "
            "for one method. Wider sections indicate "
            "relatively higher density. The inner box "
            "shows quartiles and the median.",

            "Magnitude methods can be used under "
            "different conditions. A smaller reported "
            "error does not by itself prove that a "
            "method is more accurate."
        )


    # ----------------------------------------------
    # STATISTICAL SUMMARY
    # ----------------------------------------------

    st.markdown("#### Statistical Summary")

    with st.container(
        border=True,
        key="chart_card_summary"
    ):

        if violin_data.empty:

            st.info(
                "No valid measurements match these filters."
            )

        else:

            summary = (
                violin_data
                .groupby("magType")["magError"]
                .agg(
                    Records="size",
                    Median="median",
                    Mean="mean",
                    Std_Dev="std"
                )
                .reindex(selected_methods)
                .round(3)
                .reset_index()
                .rename(columns={
                    "magType": "Method",
                    "Std_Dev": "Std. dev."
                })
            )

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Records": st.column_config.NumberColumn(
                        "Records",
                        format="%d"
                    ),
                    "Median": st.column_config.NumberColumn(
                        "Median",
                        format="%.3f"
                    ),
                    "Mean": st.column_config.NumberColumn(
                        "Mean",
                        format="%.3f"
                    ),
                    "Std. dev.": st.column_config.NumberColumn(
                        "Std. dev.",
                        format="%.3f"
                    ),
                }
            )

    st.caption(
        f"Analysis based on {len(violin_data):,} "
        "valid measurements after applying the filters."
    )


# --------------------------------------------------
# VISUALIZATION 3 — CALENDAR HEATMAP
# --------------------------------------------------

elif chosen_chart == "Calendar Heatmap":

    st.subheader("Daily Earthquake Activity Calendar")

    st.caption(
        "Explore daily M4.5+ earthquake counts. "
        "The calendar uses UTC dates, just like the source data."
    )

    # ----------------------------------------------
    # CALENDAR CONTROLS
    # ----------------------------------------------

    year_col, scope_col = st.columns(
        [1, 2],
        gap="large"
    )

    with year_col:

        calendar_year = st.selectbox(
            "Calendar year",
            options=sorted(
                df["event_date_utc"].dt.year.unique()
            ),
            key="calendar_year"
        )

    with scope_col:

        geographic_scope = st.selectbox(
            "Geographic scope",
            [
                "Global",
                "6 Feb epicentral region (approximate)"
            ],
            help=(
                "Approximate region: 35–40°N, 34–41°E. "
                "This rectangular coordinate filter is "
                "not an official aftershock catalog."
            ),
            key="calendar_scope"
        )

    # ----------------------------------------------
    # APPLY OPTIONAL REGIONAL FILTER
    # ----------------------------------------------

    calendar_data = filtered.copy()

    if geographic_scope != "Global":

        calendar_data = calendar_data.loc[
            calendar_data["latitude"].between(35, 40)
            & calendar_data["longitude"].between(34, 41)
        ].copy()

    # Preserve the sidebar's selected UTC date range.
    visible_start = min_date
    visible_end = max_date

    if isinstance(dates, (tuple, list)) and len(dates) == 2:
        visible_start, visible_end = dates

    year_data = calendar_data.loc[
        calendar_data["event_date_utc"].dt.year
        == calendar_year
    ]

    daily = (
        year_data.groupby("event_date_utc").size()
    )

    max_day_count = (
        int(daily.max())
        if not daily.empty else 0
    )

    feb6_count = int(
        daily.get(pd.Timestamp("2023-02-06"), 0)
    )

    # ----------------------------------------------
    # CALENDAR KPI METRICS
    # ----------------------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Events in selected year",
        f"{len(year_data):,}"
    )

    c2.metric(
        "Peak daily count",
        f"{max_day_count:,}"
    )

    if calendar_year == 2023:

        c3.metric(
            "6 Feb 2023 · UTC",
            f"{feb6_count:,}"
        )

    else:

        c3.metric(
            "Days with records",
            f"{len(daily):,}"
        )

    # ----------------------------------------------
    # CALENDAR CHART
    # ----------------------------------------------

    chart_col, note_col = st.columns(
        [3.5, 1.2],
        gap="large"
    )

    with chart_col:

        with st.container(
            border=True,
            key="chart_card_calendar"
        ):

            calendar_fig = create_calendar_heatmap(
                calendar_data,
                year=int(calendar_year),
                visible_start=max(
                    min_date, visible_start
                ),
                visible_end=min(
                    max_date, visible_end
                ),
                scale_max=int(
                    df["event_date_utc"].value_counts().max()
                )
            )

            calendar_fig = apply_clean_chart_style(
                calendar_fig
            )

            calendar_fig.update_yaxes(
                showgrid=False
            )

            st.plotly_chart(
                calendar_fig,
                use_container_width=True,
                config={"displaylogo": False},
                key="calendar_heatmap"
            )

    # ----------------------------------------------
    # SCIENTIFIC EXPLANATION
    # ----------------------------------------------

    with note_col:

        show_insight(
            "Each tile represents one UTC day. "
            "Darker teal means more recorded M4.5+ "
            "earthquakes. Hover over a tile for its "
            "exact event count.",

            "In the 2023 view, an amber outline marks "
            "6 February. Gray dates are outside the "
            "selected period. Colors use a logarithmic "
            "scale. The regional option uses approximate "
            "coordinates, not verified aftershock membership."
        )

    st.caption(
        "Daily counts use UTC. The colorbar shows actual "
        "event counts although colors use log(1 + count). "
        "The color scale remains fixed across years and scopes."
    )


    st.caption(
        "Dataset coverage: 1 February 2023 – 31 May 2024 (UTC). "
        "Gray cells indicate dates outside the dataset "
        "or selected range."
    )


    # ----------------------------------------------
    # MOST ACTIVE DAYS
    # ----------------------------------------------

    st.markdown("#### Most Active Days")

    with st.container(
        border=True,
        key="chart_card_calendar_summary"
    ):

        if daily.empty:

            st.info(
                "No earthquake records match this year "
                "and filter selection."
            )

        else:

            top_days = (
                daily
                .sort_values(ascending=False)
                .head(5)
                .rename_axis("UTC Date")
                .reset_index(name="Recorded Events")
            )

            top_days["UTC Date"] = (
                top_days["UTC Date"].dt.strftime(
                    "%d %b %Y"
                )
            )

            st.dataframe(
                top_days,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Recorded Events":
                        st.column_config.NumberColumn(
                            "Recorded Events",
                            format="%d"
                        )
                }
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Source: USGS ANSS Comprehensive Earthquake "
    "Catalog (ComCat) · Historical M4.5+ events · UTC."
)
