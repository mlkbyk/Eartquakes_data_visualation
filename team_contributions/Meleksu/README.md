## Member 2 – Multidimensional & Structural Visualization

**Responsible for:** Multidimensional and structural analysis of earthquake data through interactive visualizations.

### 1. Treemap – Earthquake Distribution by Location

**Purpose:** To visualize earthquake record distribution across different location labels.

- Grouped earthquake records using the `place` column.
- Calculated earthquake counts and average magnitude for each location.
- Selected the top 15 locations based on earthquake record counts.
- Used rectangle sizes to represent the number of earthquake records.
- Used color intensity to represent average earthquake magnitude.
- Added interactive hover information.

**Columns Used:**
- `place`
- `mag`
- `id`

**Libraries:** Pandas, Plotly Express (`plotly.express`)

### 2. Parallel Coordinates – Multidimensional Earthquake Analysis

**Purpose:** To examine earthquake magnitude, depth, and measurement-quality indicators simultaneously.

- Selected six numerical variables for multidimensional analysis.
- Removed records containing missing values in the selected columns.
- Represented each earthquake record as a line across parallel axes.
- Applied magnitude-based color encoding to the lines.
- Enabled interactive exploration of variable ranges through the axes.

**Columns Used:**
- `mag`
- `depth`
- `rms`
- `gap`
- `nst`
- `magError`

**Libraries:** Pandas, Plotly Graph Objects (`plotly.graph_objects`)

### 3. 3D Scatter Plot – Global Earthquake Distribution

**Purpose:** To visualize the geographical distribution and depth of earthquake records in three-dimensional space.

- Used longitude, latitude, and depth as the three spatial dimensions.
- Applied magnitude-based color encoding.
- Added location information through interactive hover details.
- Implemented a data filtering option to include or exclude earthquakes recorded at exactly 10 km depth.
- Enabled interactive rotation and zooming of the 3D visualization.

**Columns Used:**
- `longitude`
- `latitude`
- `depth`
- `mag`
- `place`

**Libraries:** Pandas, Plotly Express (`plotly.express`)

### Libraries and Tools

| Library / Tool | Purpose |
|---|---|
| Pandas | Data preprocessing, grouping, aggregation and missing-value handling |
| Plotly Express | Treemap and 3D Scatter Plot visualizations |
| Plotly Graph Objects | Parallel Coordinates visualization |
| Google Colab | Development and testing of visualizations |
| Python | Data processing and visualization logic |

### Dataset Information

- **Total records:** 9,889
- **Total columns:** 34
- **Dataset:** `earthquakes_dashboard_ready.csv`



### Research Focus

The main objective of Member 2 is to explore multidimensional relationships within earthquake data, identify geographical distribution patterns, and provide interactive visual representations of earthquake characteristics.
