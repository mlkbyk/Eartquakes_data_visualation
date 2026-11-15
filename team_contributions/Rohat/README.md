# 🌍 SEISMOSCOPE — Global Earthquake Exploratory Data Visualization & ML Analytics

**Course:** CEN445 - Introduction to Data Visualization  
**Framework:** Python, Streamlit, Plotly, Scikit-Learn  
**Dataset:** USGS Global Earthquake Catalog ($M \ge 4.5$, Feb 1, 2023 – May 31, 2024)

---

## 📌 1. Project Overview
**SEISMOSCOPE** is an interactive exploratory data visualization dashboard and machine learning analytics module designed to examine global seismic patterns, depth-magnitude hierarchies, and tectonic event clusters. In addition to global analyses, the dashboard features a dedicated spatio-temporal case study and a **Seismic Wave Propagation Simulator ($P$-Wave and $S$-Wave arrival modeling)** for the **February 6, 2023 Kahramanmaraş (Türkiye) Earthquakes** ($7.8\text{ }M_w$ Pazarcık and $7.5\text{ }M_w$ Elbistan mainshocks).

---

## 📊 2. Dataset Details & Preprocessing
* **Source:** [United States Geological Survey (USGS) Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/search/)
* **Time Span:** February 1, 2023 – May 31, 2024 (UTC)
* **Dimensions:** **9,889 rows $\times$ 34 columns** (exceeding the minimum course requirement of 2,000 rows and 7 columns).
* **Data Preprocessing & Feature Engineering:**
  * Standardized UTC timestamps and derived temporal attributes (`date_only`, `year_month`, chronological sorting).
  * Categorized continuous variables into domain-standard classes:
    * **Magnitude Categories:** `Light (4.5–4.9)`, `Moderate (5.0–5.9)`, `Strong (6.0–6.9)`, `Major (7.0+)`
    * **Depth Categories:** `Shallow (<70 km)`, `Intermediate (70–300 km)`, `Deep (>300 km)`
    * **Hemisphere:** `Northern` ($\text{latitude} \ge 0^\circ$) and `Southern` ($\text{latitude} < 0^\circ$)
  * **Spherical Coordinate Transformation:** Converted latitude and longitude into 3D unit-sphere Cartesian coordinates ($\text{geo\_x}, \text{geo\_y}, \text{geo\_z}$) and applied $\log(1 + \text{depth})$ transformation to avoid distortion near the International Date Line during machine learning training.

---

## 📈 3. Dashboard Visualizations & Special Modules

### A. Geographic & Categorical Visualizations (`app.py` - Tab 1)
1. **Multi-Mode Global Seismic Map (Geographic Map):**
   * Supports **2D Interactive Zoom Map**, **3D Orthographic Interactive Globe**, and **Monthly Temporal Animation**.
   * Encodes magnitude via color scale and exponential marker sizing, with rich hover tooltips.
2. **Multi-Stage Categorical Flow (Sankey Diagram):**
   * Visualizes proportional flow across `Magnitude Category` $\rightarrow$ `Depth Category` $\rightarrow$ `Hemisphere`.
3. **Hierarchical Seismic Distribution (Sunburst Diagram):**
   * Displays nested hierarchy (`Hemisphere` $\rightarrow$ `Magnitude Category` $\rightarrow$ `Depth Category`) colored by average magnitude ($M_w$).

### B. Statistical & Temporal Visualizations (Integrated Team Modules - Tab 2)
* Combines statistical distributions, multivariate relationships, and temporal frequency analyses across the 9 required visualization methods (3 per team member).

### C. Machine Learning Analytics (`ml/` & Tab 3)
> **Methodological Note:** These models analyze historical seismic event properties for exploratory purposes and **do not** claim to forecast future earthquake occurrences, locations, or magnitudes.

1. **Model 1 — Unsupervised K-Means Clustering ($K = 7$):**
   * **Features:** Unit-sphere coordinates ($\text{geo\_x}, \text{geo\_y}, \text{geo\_z}$), magnitude (`mag`), and $\log(1 + \text{depth})$, scaled with `StandardScaler`.
   * **Evaluation:** Trained on all 9,889 records; achieved a sample Silhouette Score of **$0.287$** across 7 distinct event-profile clusters.
2. **Model 2 — Supervised Decision Tree Classification (`depth_category`):**
   * **Target:** `depth_category` (`Shallow`, `Intermediate`, `Deep`). Raw `depth` and derived depth columns were strictly excluded from inputs to prevent data leakage.
   * **Validation Protocol:** Chronological 80/20 split (**7,911 training** events / **1,978 chronological test** events starting from `2024-02-16`) with `TimeSeriesSplit(4)` hyperparameter tuning (`max_depth=10`, `min_samples_leaf=20`, `class_weight='balanced'`).
   * **Results:** Achieved **$78.7\%$ Balanced Accuracy** (compared to **$33.3\%$** for the majority-class baseline), **$0.625$ Macro F1**, and **$69.8\%$ Overall Accuracy**.
3. **Experimental Model — Decision Tree Regression (Documented & Excluded):**
   * Attempted to predict `mag` from location and depth; yielded $\text{MAE} = 0.2643$ (worse than mean baseline $\text{MAE} = 0.2605$) and $R^2 = -0.0251$. Transparently documented and excluded from production recommendations.

### D. Feb 6, 2023 Türkiye Special Analysis & Wave Simulator (Tab 4)
* **East Anatolian Fault Zone Analysis:** Camera focus presets for Pazarcık ($7.8\text{ }M_w$), Elbistan ($7.5\text{ }M_w$), and Hatay ($6.3\text{ }M_w$) ruptures alongside magnitude-depth evolution timelines.
* **Seismic Wave Propagation Simulator:** Interactive Haversine-based physical model calculating real-time **Primary $P$-Wave ($\sim 6.0\text{ km/s}$)** and **Destructive $S$-Wave ($\sim 3.5\text{ km/s}$)** wavefront rings, impacted surface area ($\text{km}^2$), and early-warning lead times ($t_S - t_P$) across 12 surrounding provincial capitals.

---

## 🎛️ 4. Interactivity & UI Features
* **Global Sidebar Controls:** Preset presentation scenarios, date range picker, magnitude ($M_w$) slider, depth ($\text{km}$) slider, hemisphere multi-select, and filtered CSV export button.
* **Dual Adaptive Theme Engine:** Instant switching between **Light Presentation Theme** and **Soft Dark Blue Theme**.

---

## 👥 5. Team Contributions

| Team Member | Responsibilities & Contributions |
| :--- | :--- |
| **Rohat** | • Geographic & Categorical Visualizations (2D/3D/Animated Global Map, Sankey Diagram, Sunburst Chart)<br>• Machine Learning Pipeline & Evaluation (K-Means Clustering, Decision Tree Classifier, Experimental Regressor)<br>• February 6, 2023 Türkiye Special Case Study & $P$/$S$ Seismic Wave Propagation Simulator<br>• Core UI/UX Theme Engine & Dashboard Integration (`app.py`) |
| **Başak** | • Statistical Visualizations Module (`SEISMOSCOPE_Statistical_Visualizations`)<br>• Data preparation, statistical distribution charts, outlier & multivariate visual analysis<br>• Documentation and testing |
| **Meleksu** | • Temporal & Analytical Visualizations Module<br>• Repository management, main dashboard integration, and project documentation / 1-page report preparation |

---

## ⚙️ 6. Setup & Installation Instructions

### Prerequisites
* Python 3.10+ (Python 3.11 or 3.12 recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/mlkbyk/Eartquakes_data_visualation.git
cd Eartquakes_data_visualation
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
# For ML training/reproduction:
pip install -r requirements-ml.txt
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run app.py
```

### 4. (Optional) Reproduce Machine Learning Models
```bash
python -m ml.train_models
```

---

## 📂 7. Repository Structure
```text
├── app.py                              # Main Streamlit dashboard application
├── data/                               # Preprocessed USGS dataset & reference files
│   ├── earthquakes_dashboard_ready.csv
│   └── kahramanmaras_6feb_major_events_reference.csv
├── charts/                             # Modular visualization components
├── ml/                                 # Machine learning models, training scripts & reports
│   ├── models/                         # Saved .joblib pipelines
│   └── reports/                        # metrics.json, cluster_profiles.csv, ml_scored_events.csv
├── presentation_and_documentation/     # One-page report & presentation materials
├── team_contributions/                 # Individual modules by Rohat, Başak, and Meleksu
├── requirements.txt                    # Dashboard dependencies
└── README.md                           # Project documentation
```