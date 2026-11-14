# SEISMOSCOPE — ML Extension

Ready-to-use exploratory machine learning models trained on the prepared USGS dataset (9,889 rows × 34 columns, 2023-02-01 through 2024-05-31 UTC). Includes 6 February 2023 Kahramanmaraş earthquakes.

## What was trained

1. **K-Means**: seven unsupervised event-profile clusters using spherical geographic coordinates, event magnitude and log-transformed depth. Saved: `ml/models/kmeans_pipeline.joblib`.
2. **Decision Tree Classifier**: depth class (shallow/intermediate/deep) from geography and measured magnitude, with a chronological 80/20 split and time-series cross-validation on the training portion. Saved: `ml/models/decision_tree_classifier.joblib`.
3. **Experimental Decision Tree Regressor**: attempt to model magnitude from geography/depth. It performed worse than a mean-only baseline and is **not recommended as a dashboard ML result**. Saved for reproducibility and honest comparison.

See `ml/reports/RESULTS_TR.md` and `ml/reports/metrics.json` for all metrics, baselines, confusion matrix and limitations.

## Reproduce training

Use the project Python virtual environment; Python 3.13 with scikit-learn 1.8.0 has been tested for the supplied trained models. From the SEISMOSCOPE project root:

```bash
python -m pip install -r requirements.txt
python -m ml.train_models
```

This command reads `data/earthquakes_dashboard_ready.csv`, and rewrites the model and report outputs. The supplied `requirements.txt` pins `scikit-learn==1.8.0` for the saved models. Keep that version consistent across machines: pickled scikit-learn models are not guaranteed to load across incompatible versions. Do not load `.joblib` files from untrusted sources.

## Final integration in app.py

**The final `app.py` already renders this module with shared filtered records. The snippet below is explanatory; do not add it again.**

```python
from ml.ml_dashboard import render_ml_section

with st.container():
    render_ml_section(filtered_df)
```

It is already rendered inside the dashboard's Machine Learning tab. The panel contains a cluster map, cluster summary and classification confusion matrix. It never claims to forecast future events. Test metrics are from a **fixed chronological holdout** and do not change with dashboard filters.

## Important boundaries

- The ML visuals are *additional*; do not count them as a replacement for the nine distinct chart methods in the CEN445 assignment.
- K-Means cluster labels are not true plate boundaries, hazard classifications or risk predictions.
- Classification does not use measured depth or derived depth categories as input features, but the labels themselves come from recorded depths (some may be fixed at 10 km).
- Dataset / models are for historical, exploratory education only. No future earthquake predictions.
- Main data has **9,889** rows and **34** columns; preprocessing remains unchanged.
