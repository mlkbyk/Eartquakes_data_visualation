# SEISMOSCOPE | Statistical & Temporal Analysis — Member 3

This README documents **Member 3's visualization module** for the SEISMOSCOPE data visualization project. It is a component-level guide, not the README for the team's main dashboard.

## Module overview

The module implements three interactive visualization types using **Python, Pandas, Plotly, and Streamlit**:

1. **Density Contour:** earthquake magnitude versus hypocentral depth, with *Overview Contours* and *Detailed Bins* views.
2. **Violin Plot:** reported magnitude uncertainty (`magError`) by estimation method (`magType`).
3. **Calendar Heatmap:** daily counts of recorded M4.5+ earthquakes, with a February 6, 2023 highlight and optional approximate regional filtering.

All three are available in the local `preview_statistical.py` application through a **Visualization Navigator**. Only the selected visualization is displayed. The interface uses the shared *Scientific Slate* theme.

## Directory structure

```text
SEISMOSCOPE_Statistical_Visualizations/
├── .streamlit/
│   └── config.toml
├── charts/
│   ├── __init__.py
│   ├── chart_style.py
│   ├── density_contour.py
│   ├── violin_plot.py
│   ├── calendar_heatmap.py
│   └── statistical_temporal.py
├── ui/
│   ├── __init__.py
│   └── styles.py
├── data/
│   └── earthquakes_dashboard_ready.csv
├── preview_statistical.py
├── prepare_data.py                 # Optional; only if retained locally
├── requirements.txt
└── README.md
```

`charts/statistical_temporal.py` re-exports the chart functions for integration. Chart modules do not read the CSV directly; they accept filtered Pandas DataFrames and return Plotly figures. `ui/styles.py` and `charts/chart_style.py` contain the presentation styles.

The previous `density_contour_preview.html` export is **not required** and is not used by the Streamlit application.

## Data and coverage

- **Source:** U.S. Geological Survey (USGS), ANSS Comprehensive Earthquake Catalog (ComCat).
- **Local file:** `data/earthquakes_dashboard_ready.csv`.
- **Dataset size:** 9,889 earthquake records and 34 columns.
- **Coverage:** February 1, 2023 through May 31, 2024 (**UTC**).
- **Scope:** worldwide recorded earthquakes of **M4.5 or greater**.
- **Core fields used:** `mag`, `depth`, `magType`, `magError`, `event_date_utc`, `latitude`, `longitude`, and `depth_exactly_10km`.
- **Case study reference:** the two major February 6, 2023 Kahramanmaraş earthquakes are represented by USGS IDs `us6000jllz` and `us6000jlqa` in the prepared dataset.

**Coverage warning:** Gray cells in the calendar indicate dates outside the source dataset or the selected date range. They do **not** mean that no earthquakes occurred on those dates.

## Running the local preview

From the module's root folder in VS Code / Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run preview_statistical.py
```

The main dependencies are `streamlit`, `plotly`, and `pandas`. The local preview loads `data/earthquakes_dashboard_ready.csv` automatically.

### Common filters

The left sidebar contains shared filters for:

- **Magnitude range** (M4.5–M7.8 in the prepared dataset).
- **UTC date range**.
- **Include depths recorded as exactly 10 km** (a sensitivity check for catalog depth assignments).

These filters apply to the currently selected chart. Violin Plot additionally offers magnitude-method selection; Calendar Heatmap additionally offers year and geographic-scope selection.

## Visualization 1 — Density Contour

**Question:** Where are recorded earthquakes concentrated across magnitude and depth?

- **Axes:** magnitude (`mag`) and hypocentral depth in km (`depth`).
- **Overview Contours:** Plotly-selected histogram bin widths, emphasizing broader concentration patterns.
- **Detailed Bins:** fixed 0.05 magnitude-unit × 10 km depth bins, emphasizing local structure.
- **Controls:** Focused View / Full Range, shared sidebar filters, interactive hover and zoom.

Both views use the same filtered records, but their **per-bin counts are not directly comparable** because their bin sizes differ. Both views use **histogram-based contours**, not kernel density estimation (KDE).

## Visualization 2 — Violin Plot

**Question:** How does reported magnitude uncertainty vary by magnitude estimation method?

- **Fields:** `magType`, `magError`.
- **Typical methods:** `mb`, `mww`, `mwr`, when sufficient records remain.
- **Display:** violin distribution and embedded box plots (median and quartiles).
- **Controls:** multiselect for methods and shared sidebar filters.
- **Rule:** methods must have at least **30 valid `magError` values after filtering** to appear as selection options.
- **Missing values:** records without a valid nonnegative `magError` are excluded from this comparison, not from the other charts.
- **Supplement:** Statistical Summary table with sample size, median, mean, and standard deviation.

Different methods may be applied under different conditions; smaller reported uncertainty alone does not demonstrate higher measurement accuracy.

## Visualization 3 — Calendar Heatmap

**Question:** How does daily M4.5+ earthquake activity vary across the available observation period, especially on February 6, 2023?

- **Aggregation:** number of recorded events per **UTC calendar day**.
- **Controls:** 2023/2024 year selector, shared sidebar filters, and Global / approximate epicentral-region selector.
- **Regional bounds:** **35–40°N and 34–41°E** (rectangular coordinate filter).
- **Highlight:** amber outline around **February 6, 2023** in the 2023 view when that day is in the selected period.
- **Color:** logarithmic `log(1 + count)` mapping for visual contrast; hover and colorbar represent **actual daily event counts**.
- **Supplement:** *Most Active Days* table.

The approximate epicentral-region filter is **not** an authoritative aftershock catalog: earthquakes inside the rectangle must not automatically be labeled aftershocks.

## Integration with the team's dashboard

The team integration lead can copy the `charts/` module and import the following functions, provided the containing project makes `charts` importable:

```python
from datetime import date
import streamlit as st

from charts.statistical_temporal import (
    create_density_contour_smoothed,
    create_density_contour_binned,
    create_violin_plot,
    create_calendar_heatmap,
)
from charts.chart_style import apply_clean_chart_style

# `filtered_df` is the team's already-filtered earthquake DataFrame.
density_figure = create_density_contour_smoothed(filtered_df, view="Focused View")
violin_figure = create_violin_plot(filtered_df, methods=["mb", "mww", "mwr"])
calendar_figure = create_calendar_heatmap(
    filtered_df,
    year=2023,
    visible_start=date(2023, 2, 1),
    visible_end=date(2023, 12, 31),
)

# Example display:
st.plotly_chart(apply_clean_chart_style(density_figure), use_container_width=True)
```

The UI layout, shared sidebar filtering, and regional-scope selection are implemented in `preview_statistical.py` and are **not automatically added** when the functions are imported. The main dashboard should supply its own controls or adapt that preview logic. Do not duplicate the team's dataset if it already exists in the shared project.

## Validation checklist (before team handoff)

- [ ] All three charts render under default filters.
- [ ] Magnitude, UTC date, and exact-10-km filters change the displayed records correctly.
- [ ] Empty selections / zero matching records do not cause an application error.
- [ ] Violin Plot methods with fewer than 30 valid records are handled appropriately.
- [ ] Calendar day totals agree with the *Most Active Days* table and KPI cards.
- [ ] February 6, 2023 is highlighted only when included in the selected period.
- [ ] Chart labels, hover information, and regional limitations are accurate.
- [ ] Integration imports work inside the team's final project structure.

## Scientific limitations

- The catalog contains **reported M4.5+ earthquakes only**, not all earthquakes.
- Some depths reported as exactly 10 km can be assigned during earthquake-location processing; these entries are not necessarily incorrect.
- All date grouping uses UTC. Converting to Türkiye local time (UTC+3) can change which local calendar day an event falls on.
- Calendar regional counts indicate records within an approximate coordinate box, **not confirmed aftershock membership**.
- Distributions and results describe the selected catalog and filters; they should not be treated as causal conclusions.

## Attribution

U.S. Geological Survey (USGS), ANSS Comprehensive Earthquake Catalog (ComCat): https://earthquake.usgs.gov/earthquakes/search/
