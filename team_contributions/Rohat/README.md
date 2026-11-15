# SEISMOSCOPE - Geographic Visualizations, ML Pipeline & Wave Simulator (Rohat)

This folder contains my individual code and model outputs for the **SEISMOSCOPE** dashboard (CEN445 Introduction to Data Visualization). In this part of the project, I worked on the geographic and categorical charts, trained the machine learning models, and built the February 6, 2023 Kahramanmaraş earthquake analysis tab with a wave propagation simulator.

## 1. Data Preparation
We used the USGS Global Earthquake dataset ($M \ge 4.5$, from February 1, 2023 to May 31, 2024), which has **9,889 rows and 34 columns**. For my modules, I added a few extra columns and transformations:
* **Magnitude bins (`mag_cat_col`):** `Light (4.5-4.9)`, `Moderate (5.0-5.9)`, `Strong (6.0-6.9)`, and `Major (7.0+)`.
* **Depth bins (`depth_cat_col`):** `Shallow (<70 km)`, `Intermediate (70-300 km)`, and `Deep (>300 km)`.
* **Hemisphere (`hemisphere_col`):** Split at the equator ($\text{latitude} \ge 0^\circ$ as Northern, $\text{latitude} < 0^\circ$ as Southern).
* **Spherical coordinates:** Converted latitude and longitude into 3D unit-sphere coordinates (geo_x, geo_y, geo_z) and took log1p(depth) for clustering so events near the +-180 date line are not separated artificially.

## 2. My 3 Core Visualizations (Tab 1)
To cover the geographic and categorical part of our team's 9 charts, I built three interactive Plotly charts in `app.py`:

1. **Global Earthquake Map (`px.scatter_map` / `px.scatter_geo`):**
   * Includes a radio button to switch between a 2D zoomable map, a 3D orthographic globe, and a monthly time animation (`year_month`).
   * Point sizes are scaled exponentially from magnitude so strong earthquakes stand out clearly against regular 4.5-5.0 events.
2. **Categorical Flow Chart - Sankey Diagram (`go.Sankey`):**
   * Tracks how earthquake counts flow from `Magnitude Category` $\rightarrow$ `Depth Category` $\rightarrow$ `Hemisphere`.
   * Makes it easy to see that most moderate and strong earthquakes happen at shallow depths ($< 70\text{ km}$).
3. **Hierarchical Breakdown - Sunburst Chart (`px.sunburst`):**
   * Groups records from the inside out (`Hemisphere` $\rightarrow$ `Magnitude Category` $\rightarrow$ `Depth Category`) and colors each slice by its mean magnitude ($M_w$).

## 3. Machine Learning Module (`ml/` & Tab 3)
*Note: These models are only used to explore patterns in past earthquakes from our dataset. They do not predict future earthquakes.*

* **K-Means Clustering (K = 7):**
  * Trained on all 9,889 events using scaled unit-sphere coordinates (geo_x, geo_y, geo_z), `mag`, and log1p(depth).
  * Tested K = 3 to 7 on a fixed 1,500-event sample and picked K = 7 with a silhouette score of 0.287.
* **Decision Tree Classifier (`depth_category`):**
  * Predicts whether an earthquake is shallow, intermediate, or deep using only location and magnitude (raw depth columns were left out to avoid data leakage).
  * Used an 80/20 chronological split (**7,911 train** / **1,978 test** starting from `2024-02-16`) and tuned with `TimeSeriesSplit(4)` (`max_depth=10`, `min_samples_leaf=20`, `class_weight='balanced'`).
  * Reached 78.7% Balanced Accuracy (0.625 Macro F1, 69.8% Overall Accuracy) vs. 33.3% balanced accuracy for a majority-class baseline.
* **Decision Tree Regressor (Dropped Experiment):**
  * Tried predicting mag from location and depth, but got MAE = 0.2643 and R2 = -0.0251 (worse than simply guessing the mean with MAE = 0.2605). I kept the logs in RESULTS_TR.md for transparency but excluded it from the final dashboard.

## 4. Feb 6, 2023 Türkiye Case Study & Wave Simulator (Tab 4)
* Filters the catalog down to the Türkiye region (35.5-42.5 N, 25.5-45.0 E) with quick camera presets for the Pazarcık (7.8 Mw), Elbistan (7.5 Mw), and Hatay (6.3 Mw) ruptures.
* **P & S Wave Simulator:** Uses Haversine distances and hypocentral depth to calculate how far primary P-waves (~6.0 km/s) and destructive S-waves (~3.5 km/s) travel after t seconds (5-110 s slider). It draws live wave rings on the map and lists arrival times for 12 nearby cities.

## 5. How to Run Locally
Install the required packages and start the Streamlit app from this directory:

```bash
pip install -r requirements-ml.txt
streamlit run app.py
```

To retrain the models and regenerate the `.joblib` files and reports from scratch:

```bash
python -m ml.train_models
```

## 6. Files in This Folder
* `app.py` - Standalone Streamlit dashboard with my visualizations, sidebar filters, ML results tab, and the Türkiye wave simulator.
* `data/` & `earthquake_project_feb6/` - Processed dataset (`earthquakes_dashboard_ready.csv`) and Feb 6 reference events.
* `ml/` - Model training scripts, saved `.joblib` pipelines, `cluster_profiles.csv`, and `ml_scored_events.csv`.
* `README_ML.md` & `RESULTS_TR.md` - Technical notes and test metrics for the machine learning experiments.
* `requirements-ml.txt` - Python dependencies.
