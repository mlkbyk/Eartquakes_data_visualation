# SEISMOSCOPE

### Interactive Earthquake Data Exploration & Machine Learning

**CEN445 — Introduction to Data Visualization · Team project · Python / Streamlit / Plotly / scikit-learn**

SEISMOSCOPE is an interactive educational dashboard for exploring historical earthquake records. It brings together **nine distinct visualizations (three per team member)**, shared data filters, two trained exploratory machine-learning models, and a dedicated study of the **6 February 2023 Kahramanmaraş earthquakes in Türkiye**.

> **Status:** Integrated dashboard; the three visualization modules have been manually reviewed, and all **15 shared automated visualization tests passed** on 14 November 2026. The dataset/ML integrity validation also passed. This is an educational exploration tool, **not** an earthquake forecast, an official aftershock catalog, a hazard map, a damage estimator, or an emergency-warning service.

## Dataset and source

| Property | Description |
|---|---|
| Source | [USGS ANSS Comprehensive Earthquake Catalog (ComCat)](https://earthquake.usgs.gov/earthquakes/search/) |
| File | [`data/earthquakes_dashboard_ready.csv`](data/earthquakes_dashboard_ready.csv) |
| Records and fields | **9,889 rows × 34 columns** (22 catalog fields and 12 derived fields) |
| Time span | **1 February 2023 – 31 May 2024**, inclusive, UTC |
| Geographic scope | Worldwide, recorded earthquakes **M4.5+** |
| Geographic coordinates | Latitude/longitude in decimal degrees; depth in kilometers |
| Mainshock references | [`data/kahramanmaras_6feb_major_events_reference.csv`](data/kahramanmaras_6feb_major_events_reference.csv) |

The reviewed dataset retains the measured catalog values and does **not** create synthetic substitute earthquakes or impute missing optional measurements. The event IDs are unique. **4,380 of 9,889 records** report depth exactly **10 km**; a sensitivity filter allows these records to be excluded without claiming they are all erroneous. For details, see [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md), [`docs/VERI_KALITE_RAPORU.md`](docs/VERI_KALITE_RAPORU.md) and [`docs/quality_metrics.json`](docs/quality_metrics.json).

Two documented main events are included:

| Event | USGS ID | UTC time (6 Feb 2023) | Magnitude | Reported depth |
|---|---|---|---:|---:|
| Pazarcık | [`us6000jllz`](https://earthquake.usgs.gov/earthquakes/eventpage/us6000jllz) | 01:17:34 | M7.8 | 10.000 km |
| Elbistan | [`us6000jlqa`](https://earthquake.usgs.gov/earthquakes/eventpage/us6000jlqa) | 10:24:48 | M7.5 | 7.432 km |

The USGS `mag` field can reflect different estimation methods (`magType`), so the app does **not** assume every reported magnitude is measured on an identical `Mw` scale.

## Dashboard: six sections

The **Seismic Intelligence** interface uses a navy/teal/slate design and presents these sections:

| Section | Visualizations / functionality | Team responsibility |
|---|---|---|
| **Overview** | Catalog context, monthly record counts, global epicenter view, historical-event spotlight | Integrated view |
| **Geographic** | **Geographic Map** (2D, orthographic globe, monthly animation), **Sankey Diagram**, **Sunburst** | Member 1 |
| **Statistical & Temporal** | **Density Contour** (overview and detailed versions), **Violin Plot**, **Calendar Heatmap** | Member 3 |
| **Multidimensional & 3D** | **Treemap**, **Parallel Coordinates**, **3D Scatter** | Member 2 |
| **Machine Learning** | Saved K-Means/Decision Tree results and inference on a selected historical catalog event | Shared / see credits below |
| **Türkiye · February 2023** | Historical Events, Regional Analysis and idealized P/S Wave Simulation | Shared / see credits below |

Shared sidebar controls include **magnitude range, UTC date range, hemisphere** and the **include-exactly-10-km-depth** checkbox. Plotly charts offer appropriate interactions, such as hovering, panning, zooming, category selection, brushing, rotation or animation. The Türkiye case-study tab has its **own** date window so its historical reference remains available independently of global filters.

## Exploratory machine learning

ML analyses are additional to the nine visualization methods. Training source, saved models, and fixed evaluation reports are included under [`ml/`](ml/).

**K-Means clustering:** standardized geographic unit-sphere coordinates, catalog magnitude and log-depth; **K = 7** chosen from K = 3–7; sampled silhouette score **0.287**. The clustering model was fitted to all **9,889** records. Clusters describe historical similarities, **not** risk classes or tectonic boundaries.

**Decision Tree classification:** predicts the **cataloged depth class** (shallow / intermediate / deep) using geographic coordinates and magnitude, without measured depth as an input. Chronological **7,911 train / 1,978 holdout** split. Held-out **accuracy 69.8%**, **balanced accuracy 78.7%**, **macro F1 0.625**. The majority-class baseline achieves **77.6% overall accuracy**; the tree performs better for class balance but **not** for raw accuracy. The dashboard's evaluation metrics come from the fixed holdout; filtering the current view does not retrain the model.

An experimental magnitude regressor is retained as a reproducibility artifact but **excluded from the main results** because it did not beat its baseline. See [`docs/ML_METHODS_AND_RESULTS.md`](docs/ML_METHODS_AND_RESULTS.md) and [`ml/reports/metrics.json`](ml/reports/metrics.json).

**Saved-model compatibility:** the provided `.joblib` estimators were trained using **scikit-learn 1.8.0**. The supplied `requirements.txt` pins this version. Load only model files from a trusted source.

## Türkiye 2023 and wave demonstration

The February 6 area uses documented historical reference records. The **Regional Analysis** covers an approximate geographic rectangle and user-selected UTC dates; events inside that rectangle **must not** automatically be called confirmed aftershocks.

The **Wave Simulation** illustrates idealized P/S travel-time geometry using constant assumed speeds of **6.0 km/s (P)** and **3.5 km/s (S)**, with city-center distances and adjustable elapsed time. It **does not** model real shaking, damage, building exposure, earthquake propagation through realistic geology or operational early warning.

## Project structure

```text
SEISMOSCOPE/
├── app.py                         # Final Streamlit entry point
├── charts/
│   ├── geographic/                # Member 1 integrated charts
│   ├── multidimensional/          # Member 2 integrated charts
│   └── statistical/               # Member 3 integrated charts
├── data/                          # Prepared USGS CSV + 6 Feb reference CSV
├── ml/
│   ├── features.py
│   ├── ml_dashboard.py
│   ├── train_models.py
│   ├── models/                    # Saved trained joblib estimators
│   └── reports/                   # ML metrics, profiles, scored records
├── scripts/                       # Data preparation and validation
├── tests/                         # 15 shared unittest checks
├── docs/                          # Technical documentation and data quality notes
├── presentation_and_documentation/
│   ├── SEISMOSCOPE_Project_Report.pdf
│   ├── SEISMOSCOPE_Project_Presentation.pptx
│   └── SEISMOSCOPE_Project_Presentation.pdf  # Optional PDF version
├── team_contributions/            # Members upload independent source folders
│   ├── Başak\SEISMOSCOPE_Statistical_Visualizations/
│   ├── Meleksu\SEISMOSCOPE_Multidimensional_Visualizations/
│   └── Rohat\SEISMOSCOPE_Geographic_Categorical_Visualizations/
├── .streamlit/config.toml
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

The `charts/` modules are the visualizations used by the integrated application. The `team_contributions/` folders separately document each member's independent work and will be uploaded by the corresponding members. The contribution folders shown above describe the intended final layout; some may not appear until their owners commit them.

Local `.venv/`, `backups/`, Python caches and temporary ZIP packages should **not** be committed or included in submission archives.

## Installation and running (Windows PowerShell)

**Recommended:** Python **3.13** (tested in the project environment); packages are installed from `requirements.txt`. In the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`). Using the venv interpreter directly avoids Windows execution-policy issues. A network connection may be needed to load map tiles. No private API key is required for the reviewed local dataset.

## Validation and reproducibility

Run the checks from the project root:

```powershell
.\.venv\Scripts\python.exe -m scripts.validate_project
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

**Last verified, 14 November 2026:** dataset and ML integrity checks **PASS**, and **15/15 visualization unit tests PASS**. Visual user-interface testing was also performed on the six dashboard sections. Some functionality depends on the graphical browser and should be checked during the final demo.

Re-training is **optional** and overwrites existing model/report artifacts:

```powershell
.\.venv\Scripts\python.exe -m ml.train_models
```

Rebuilding the prepared catalog requires the original USGS export file and should not be confused with ordinary installation. The reviewed CSV is already included.

## Team Members and Contributions

SEISMOSCOPE is a collaborative data visualization project developed by three Computer Engineering students. The visualization responsibilities below reflect the team's agreed division of work.

| Contributor | Visualization area | Implemented visualizations |
|---|---|---|
| **Member 1 — Rohat Sarıgül** | Geographic & Categorical Analysis | Geographic Map (2D, Orthographic Globe, Monthly Animation); Sankey Diagram; Sunburst Chart |`2022556051` |
| **Member 2 — Meleksu Böyük** | Multidimensional & 3D Analysis | Treemap; Parallel Coordinates; 3D Scatter Plot | `2022556015` |
| **Member 3 — Başak Karaman** | Statistical & Temporal Analysis | Density Contour (Overview Contours and Detailed Bins); Violin Plot; Calendar Heatmap | `2022556038` |

The final integrated dashboard combines all nine member visualizations with exploratory machine-learning results and the 6 February 2023 Türkiye case study. Shared tasks such as data preparation, ML training, dashboard integration and documentation should be credited to the individuals who actually carried them out; no individual attribution for these tasks is asserted here.

## Scientific limitations

- This is a worldwide **M4.5+** historical catalog, not an inventory of all earthquakes.
- Optional measurements may be absent; some charts use complete-case subsets.
- Reported **10 km** depths can reflect catalog practices and should be interpreted cautiously.
- USGS `place` labels are descriptive, not standardized administrative regions.
- The catalog spans **11 months in 2023** and **5 months in 2024**; raw annual counts are not directly comparable annualized rates.
- Clustering and classification do **not** forecast future earthquakes, damage, or hazard.
- Neither a rectangular geographic selection nor the wave simulation identifies verified aftershocks or measures real-world damage.

## Course submission

**CEN445 Introduction to Data Visualization (26 October 2026 assignment):** public GitHub repository, English one-page report including the GitHub URL, and an **English team presentation** at the allocated date/time. The assignment deadline is **15 November 2026, 23:59**. Confirm the expected file upload fields in the [Microsoft Form](https://forms.cloud.microsoft/r/2k8uhA1knE).

- **GitHub repository (make public before submission):** [mlkbyk/Eartquakes_data_visualation](https://github.com/mlkbyk/Eartquakes_data_visualation)
- **Project report (one page, English):** [SEISMOSCOPE_Project_Report.pdf](presentation_and_documentation/SEISMOSCOPE_Project_Report.pdf)
- **Project presentation (PowerPoint, English):** [SEISMOSCOPE_Project_Presentation.pptx](presentation_and_documentation/SEISMOSCOPE_Project_Presentation.pptx)
- **Presentation (PDF copy):** [SEISMOSCOPE_Project_Presentation.pdf](presentation_and_documentation/SEISMOSCOPE_Project_Presentation.pdf) 

The repository must be **public at submission time**. Presentation materials are included for convenient review, although the assignment does not explicitly require the slide deck to be stored on GitHub. All three members should verify their individual source folders are uploaded before the final submission.

### Attribution

Data: **USGS ANSS Comprehensive Earthquake Catalog (ComCat)** — https://earthquake.usgs.gov/earthquakes/search/. USGS does not endorse this student dashboard. Team-authored code, charts and documents should be attributed to their actual authors.
