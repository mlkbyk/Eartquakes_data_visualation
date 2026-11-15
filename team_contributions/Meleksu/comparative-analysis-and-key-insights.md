Responsible for: Multidimensional and Structural Analysis of Earthquake Data Using Interactive Visualization.

Note: Same dataset (earthquakes_dashboard_ready.csv) was used by all team members to keep the repository clean without any duplicates.

Treemap Analysis – Region-wise Frequencies & Average Magnitude

Highest Seismic Frequency: The region with the highest frequency of earthquake is the South Sandwich Islands with the highest number of earthquake records (317 records), then comes the Izu Islands, Japan region (232 records) and southeast of the Loyalty Islands (228 records).

Difference between Frequency & Severity: More earthquake record does not imply that average magnitude will be high. For example:

High Frequency, Low Average Magnitude: The regions such as south of the Fiji Islands (185 records) and Fiji region (87 records) have relatively low average magnitude (approx. 4.70 - 4.72).

Low Frequency, High Average Magnitude: The regions like the central Mid-Atlantic Ridge (77 records), Kermadec Islands, New Zealand (136 records), and southeast of the Loyalty Islands (228 records) have relatively high average magnitudes (approx. 4.82 - 4.85).

Parallel Coordinates Analysis: Relationships and Measurements in Multiple Dimensions

Relationship between Magnitude & Depth Distribution: Earthquakes with larger magnitudes (> 6.5, represented by orange and yellow colors) are located in shallower depths (< 150 km) compared to deep focus earthquakes, which are located in 300 km - 650 km depth intervals in moderate magnitudes of 4.5 - 6.0.

Number of Station Coverage (nst) & Azimuthal Gap (gap): Large magnitudes are registered by more seismic stations (100 - 450 + stations). This results in a smaller Azimuthal Gap (< 100°) that means better geographical coverage of an epicenter.

Measurement Quality (rms & magError): With more station coverage, uncertainties become smaller. Larger magnitudes recorded by many stations with small azimuthal gap have smaller Magnitude Error (< 0.15).

### 3. Comparison of 3D Scatter Plot: Effect of Filtering the 10 km Fixed Depth in Global Seismic Catalogs

In global seismic catalogs, when the precise focal depth of a shallow earthquake cannot be determined accurately, a default value of 10 km may be assigned.

As seen from the comparison of both figures, the structural significance of this filtering becomes clear:

| Filtering Condition | Structural and Visual Feature | Analytical Significance |
|---|---|---|
| **With 10 km Depth Included (`show_10km = True`)** | Generates an artificial, dense cluster at the 10 km depth level along oceanic ridges and continental fault zones. | Helps visualize the full spatial pattern of global seismic events, including records with uncertain depth estimates. |
| **Without 10 km Depth (`show_10km = False`)** | Removes the artificial clustering at 10 km and displays earthquakes with unconstrained depth values. | Helps reveal the actual 3D underground structure of subduction zones (Wadati-Benioff zones), with steeply dipping planes extending beyond 600 km in the Tonga-Kermadec and Japan trenches. 

### Visualization Performance & Optimization

**Grouping Records Before Aggregation & Filtering:** The Treemap displays the top 15 regions based on earthquake record counts. Incomplete records are excluded from the relevant visualizations using `dropna()`.

**WebGL:** The Parallel Coordinates and 3D Scatter Plot visualizations benefit from Plotly's hardware acceleration through WebGL, enabling interactions such as rotation, zooming, and brushing across thousands of multidimensional data points.

**Marker Size & Transparency:** Marker sizes are set to 3, with transparency (`opacity`) set to 0.75.

