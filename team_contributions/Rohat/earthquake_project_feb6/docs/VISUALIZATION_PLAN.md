# SEISMOSCOPE — Nine Visualizations + Two ML Analyses

**All concepts use the prepared 9,889-row USGS dataset.** This is a design plan, not a claim that the nine charts have already been implemented. The instructor decides which chart methods count as advanced; validate six accepted types before submission.

| # | Method | Advanced candidate? | Distinct analytical question | Main data fields | Intended interactivity |
|---|---|---|---|---|---|
| 1 | **Interactive geospatial scatter map** | Yes | Where are the largest recorded earthquakes concentrated? | latitude, longitude, mag, time | Pan, zoom, marker hover, magnitude/date filters |
| 2 | **Sankey diagram** | Yes | How do magnitude classes flow into depth classes and hemispheres? | magnitude_band, depth_category, latitude_hemisphere | Hover flow counts, category selection |
| 3 | **Sunburst hierarchy** | Yes | How does magnitude mix vary among latitude bands within each hemisphere? | latitude_hemisphere, latitude_band, magnitude_band | Click-to-drill, hover, category filters |
| 4 | **Treemap** | Yes | Which named places/regions account for the largest numbers of catalog records? | place, mag | Hover counts and mean magnitude, top-N slider |
| 5 | **Parallel coordinates** | Yes | How do magnitude, depth and measurement-quality metrics vary together? | mag, depth, rms, gap, nst, magError | Axis brushing, color by magnitude |
| 6 | **3D scatter** | Yes | How are hypocenter depths distributed across global coordinates? | latitude, longitude, depth, mag | 3D rotate/zoom, hover, hide 10-km values checkbox |
| 7 | **2D density contour** | Yes | Where do magnitude and depth measurements cluster? | mag, depth, depth_exactly_10km | Contour hover/zoom, 10-km sensitivity toggle |
| 8 | **Violin distribution** | May be categorized advanced | How do magnitude uncertainty distributions differ between magnitude calculation methods? | magType, magError | Group selection, box overlay, hover |
| 9 | **Calendar heatmap** | Yes | When were M4.5+ events concentrated, and what changes around 6 February 2023 in a defined southeast Türkiye region? | event_date_utc, id | Calendar period filters, hover daily counts, highlighted 6 February 2023 marker and selectable regional scope |

**Dashboard filter controls (≥3):** date range, magnitude range, depth category multiselect, latitude band multiselect, 10-km depth sensitivity toggle. All compatible visuals should respond to shared filters.

**Avoid duplicated insights:** (2) focuses on categorical transitions, (3) on hierarchical latitudinal composition, (4) on the most frequently named catalog locations; (1) is an exact coordinate map, (6) explores vertical hypocenter structure, (7) is a statistical joint distribution, and (9) shows temporal bursts.

**Accessibility and interpretation:** Show axes/units and legends. Display the active count (n) on each graph. All maps express *recorded M4.5+ events*, not earthquake risk. 'place' is a descriptive USGS label, not a normalized country field. 10-km depths may be fixed values. Work in UTC for time-based analysis.

## Basic machine learning extensions (suggested, NOT implemented)

1. **K-Means clustering** of event profiles. Start with latitude/longitude represented as spherical 3D coordinates (avoids anti-meridian discontinuity), magnitude, depth (scaled). Explain scaling and cluster interpretation; silhouette score for cluster counts.
2. **Decision Tree Classification** of depth group (shallow/intermediate/deep), using latitude/longitude (represented on a sphere), magnitude and optional quality metrics. Exclude raw `depth`, `depth_category`, and `depth_exactly_10km` from input features to prevent target leakage. Use stratified train/test and report class-weighted metrics; treat results as exploratory, not forecasting.

Both ML ideas are **exploratory associations**, not predictions of the location/time of future earthquakes. Evaluate whether any chosen target is scientifically meaningful before finalizing.

## 6 February 2023 Kahramanmaraş focus

- Use `id` values `us6000jllz` (M7.8) and `us6000jlqa` (M7.5) to **highlight exact, verified events** on the interactive map (chart 1) and in the calendar/day chart (chart 9).
- Add a sidebar regional toggle (e.g. latitude 35.5–39.5°N / longitude 35–40.5°E) to zoom to southeast Türkiye. Call it an *illustrative coordinate window*, not a formal fault/aftershock boundary.
- Use time-series counts of **cataloged M4.5+ earthquakes**, with UTC vs Türkiye UTC+3 noted.
- Do not call every post-February-6 event an aftershock unless independently verified; all observed concentrations are descriptive.
- Preserve exactly nine **distinct types** for the assignment: showing a zoomed map and a global map are alternative views of chart 1, not two different chart methods.
- Distinguish global patterns from the region-specific Feb 6 story; use shared filters but clear captions about the selected subset.
