# SEISMOSCOPE | Multidimensional & 3D Analysis — Member 2

This README documents **Member 2's visualization module** for the SEISMOSCOPE data visualization project. It describes the implementation of three interactive visualizations designed to explore earthquake distributions and relationships between multiple earthquake parameters.

## Module Overview

The module implements three visualization types using **Python, Pandas, Plotly, and Streamlit integration**:

1. **Treemap:** displays the most frequent earthquake location labels, with rectangle areas representing earthquake counts and colors representing average magnitude.
2. **Parallel Coordinates:** visualizes six earthquake parameters simultaneously to explore multidimensional patterns and measurement characteristics.
3. **3D Scatter Plot:** represents earthquake records using longitude, latitude, and depth, with magnitude encoded by color.

The chart functions receive Pandas DataFrames and return Plotly figures. They are integrated into the main SEISMOSCOPE dashboard.

## Directory Structure

```text
charts/
└── multidimensional/
    ├── __init__.py
    ├── multidimensional.py
    ├── treemap.py
    ├── parallel_coordinates.py
    └── scatter_3d.py
```

- `treemap.py` contains the location aggregation and Treemap implementation.
- `parallel_coordinates.py` contains the measurement preparation and Parallel Coordinates implementation.
- `scatter_3d.py` contains the 3D data preparation and scatter plot implementation.
- `multidimensional.py` exposes the chart functions for integration into the main application.

## Data Handling

The module uses the earthquake DataFrame provided by the main application rather than loading the dataset independently.

The visualizations use different subsets of the available columns:

| Visualization | Required columns |
|---|---|
| Treemap | `place`, `mag`, `id` |
| Parallel Coordinates | `mag`, `depth`, `rms`, `gap`, `nst`, `magError` |
| 3D Scatter Plot | `latitude`, `longitude`, `depth`, `mag`, `place` |

Each visualization performs its own data preparation and validation.

## Visualization 1 — Treemap

**Question:** Which reported earthquake locations contain the highest number of records, and how does their average magnitude differ?

- **Visualization type:** Interactive Treemap.
- **Grouping:** Earthquake records are grouped by the `place` field.
- **Default selection:** Top 15 locations based on earthquake count.
- **Rectangle area:** Number of earthquake records (`earthquake_count`).
- **Color:** Average recorded magnitude (`avg_magnitude`).
- **Interaction:** Hover information displays the location label, earthquake count, and average magnitude.
- **Customization:** The number of displayed locations can be changed using the `top_n` parameter.
- **Color palettes:** Member 2 final palette and `RdYlBu_r`.

The `summarize_locations()` function performs the aggregation. It counts records using the `id` field, calculates the average magnitude for each location, sorts locations by earthquake count in descending order, and returns the selected Top-N results.

The `create_treemap()` function uses this summary to generate the interactive Plotly visualization.

The Treemap provides a compact comparison of frequently reported earthquake locations. Its grouping is based on location labels and does not represent a nested country-region-city hierarchy.

## Visualization 2 — Parallel Coordinates

**Question:** How do multiple earthquake parameters vary together across recorded earthquake events?

- **Visualization type:** Parallel Coordinates Plot.
- **Number of dimensions:** Six.
- **Parameters:**
  - `mag`: Magnitude.
  - `depth`: Hypocentral depth (km).
  - `rms`: Root Mean Square (s).
  - `gap`: Azimuthal gap (°).
  - `nst`: Number of stations.
  - `magError`: Magnitude uncertainty.
- **Line representation:** Each polyline represents one earthquake record.
- **Color encoding:** Magnitude, using the `FINAL_SCALE` color gradient.
- **Interaction:** Plotly provides interactive exploration of the axes and individual lines.

### Data Preparation

The `complete_measurements()` function:

- Checks whether all six required columns exist.
- Converts their values to numeric format.
- Treats values that cannot be converted as missing.
- Removes records that contain missing values in any of the six measurements.

Only records with complete measurements across all six dimensions are included in the visualization.

If no complete records remain, the chart displays an explanatory message instead of an empty plot.

The Parallel Coordinates visualization makes it possible to examine multiple earthquake measurements together, including magnitude, depth, and measurement-quality-related parameters.

## Visualization 3 — 3D Scatter Plot

**Question:** How are recorded earthquakes distributed geographically and across different focal depths?

- **Visualization type:** Interactive 3D Scatter Plot.
- **X-axis:** Longitude (°).
- **Y-axis:** Latitude (°).
- **Z-axis:** Hypocentral depth (km).
- **Color:** Earthquake magnitude (`mag`).
- **Point representation:** Each point represents an earthquake record.
- **Hover information:** Location label, latitude, longitude, depth, and magnitude.
- **Interaction:** Rotation, zooming, and hover-based inspection.
- **Depth orientation:** The depth axis is reversed to display the depth direction appropriately.
- **Marker settings:** Marker size and opacity can be configured.

The `prepare_3d_data()` function checks the required columns and removes records with missing values in the fields used by the visualization.

### Fixed 10 km Depth Comparison

The 3D Scatter Plot includes an optional parameter:

`include_exact_10km`

- When `True`, records with a reported depth of exactly 10 km are included.
- When `False`, records with a depth equal to 10.0 km are excluded.

This option allows the spatial distribution to be examined under two different filtering conditions.

The comparison focuses on:

- Changes in the visible distribution of earthquake records.
- Differences in the depth structure.
- The effect of excluding records reported at exactly 10 km.
- Changes in the interpretation of the displayed earthquake distribution.

A reported depth of exactly 10 km does not necessarily indicate an incorrect measurement. Such values may reflect default or constrained depth assignments in earthquake catalogs. Therefore, this comparison is treated as a sensitivity check rather than a correction of the original dataset.

## Dashboard Integration

The visualization functions are exposed through the multidimensional chart module for use by the main application.

The public functions include:

```python
from charts.multidimensional.multidimensional import (
    create_treemap,
    summarize_locations,
    create_parallel_coordinates,
    complete_measurements,
    create_scatter_3d,
    prepare_3d_data
)
```

The main dashboard calls these functions to display the corresponding Plotly figures.

The chart module is responsible for data preparation and figure generation, while the main application handles dashboard navigation, shared filtering, and chart presentation.


## Scientific Limitations

- The Treemap groups records using the reported `place` text. Similar geographical locations with different labels may appear as separate categories.
- The Treemap displays only the selected Top-N locations, not necessarily the complete set of location labels.
- Parallel Coordinates excludes records missing any of its six required measurements. Consequently, its displayed sample may differ from those of the other visualizations.
- Parallel Coordinates can become visually crowded when many earthquake records are displayed.
- The 3D Scatter Plot may contain overlapping points, making some individual records difficult to distinguish.
- Excluding exact-10-km records does not establish that the excluded depths were inaccurate.
- The visualizations describe patterns in the selected earthquake catalog and should not be interpreted as evidence of causal relationships.

## Attribution

U.S. Geological Survey (USGS), ANSS Comprehensive Earthquake Catalog (ComCat):

https://earthquake.usgs.gov/earthquakes/search/
