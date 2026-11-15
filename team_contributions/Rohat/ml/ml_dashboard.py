"""Streamlit ML panel. Add from ml.ml_dashboard import render_ml_section.

Uses pre-computed scores, fixed held-out metrics and the SAME 'id' identifiers
as the prepared USGS file. This section supplements the nine main chart types.
"""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / 'ml' / 'reports'


def render_ml_section(filtered_df: pd.DataFrame) -> None:
    """Render K-Means clusters and Decision Tree classification report in Streamlit.

    Parameters
    ----------
    filtered_df : DataFrame
        Dataset after applying dashboard filters; must include 'id'.
    """
    import streamlit as st

    st.header('Machine Learning — Exploratory Analyses')
    st.caption('Historical M4.5+ USGS earthquake records only. These models do not predict future earthquakes or hazard.')
    with open(REPORTS/'metrics.json', encoding='utf-8') as f:
        metrics = json.load(f)
    scored = pd.read_csv(REPORTS/'ml_scored_events.csv', usecols=['id','kmeans_cluster'])
    if 'id' not in filtered_df.columns:
        st.error("The main DataFrame must include the 'id' column.")
        return
    merged = filtered_df.merge(scored, on='id', how='left', validate='one_to_one')
    merged = merged.dropna(subset=['kmeans_cluster','latitude','longitude','mag','depth']).copy()
    if merged.empty:
        st.info('No events match the current filters.')
        return
    merged['kmeans_cluster'] = merged['kmeans_cluster'].astype(int).astype(str)

    st.subheader('1. K-Means: Historical Event Profiles')
    cluster_metrics = metrics['kmeans']
    st.write(f"Groups: **{cluster_metrics['selected_k']}** · "
             f"Sample silhouette score: **{cluster_metrics['silhouette_search'][str(cluster_metrics['selected_k'])]['silhouette_sample']:.3f}**")
    st.caption('Colors are exploratory data groups, not plate boundaries or hazard zones. ' 
               'Cluster labels reflect geography, magnitude and log-depth. The map follows the dashboard filters.')
    fig = px.scatter_geo(
        merged, lat='latitude', lon='longitude', color='kmeans_cluster',
        hover_name='place' if 'place' in merged.columns else None,
        hover_data={'mag':':.1f','depth':':.1f','kmeans_cluster':True},
        title='USGS event clusters (filtered view)',
        projection='natural earth',
    )
    fig.update_traces(marker={'size':4,'opacity':0.65})
    fig.update_layout(margin={'l':0,'r':0,'t':45,'b':0},legend_title_text='Cluster')
    st.plotly_chart(fig, use_container_width=True, key='ml_clusters_map')
    profiles = pd.read_csv(REPORTS/'cluster_profiles.csv')
    st.dataframe(profiles.rename(columns={
        'cluster':'Cluster','count':'Records','avg_mag':'Mean magnitude',
        'median_depth_km':'Median depth (km)','avg_depth_km':'Mean depth (km)',
        'north_fraction':'Northern-hemisphere share','share_pct':'Share (%)'
    }).round(3), use_container_width=True, hide_index=True)

    st.subheader('2. Decision Tree: Recorded Depth Class')
    c = metrics['decision_tree_classification']
    col1, col2, col3 = st.columns(3)
    col1.metric('Balanced accuracy',f"{c['test_balanced_accuracy']:.1%}")
    col2.metric('Macro F1',f"{c['test_macro_f1']:.3f}")
    col3.metric('Overall accuracy',f"{c['test_accuracy']:.1%}")
    st.caption(f"Chronological holdout: {metrics['dataset']['test_rows']:,} later events. "
               f"A majority-class baseline has {c['baseline_majority_test_accuracy']:.1%} overall accuracy "
               f"but only {c['baseline_majority_test_balanced_accuracy']:.1%} balanced accuracy. "
               'Test scores here are FIXED and do not change with page filters.')
    classes = c['classes']
    conf = c['confusion_matrix_rows_actual_cols_predicted']
    matrix = go.Figure(go.Heatmap(
        z=conf, x=classes, y=classes, colorscale='Blues',
        text=conf, texttemplate='%{text}', hovertemplate='Actual: %{y}<br>Predicted: %{x}<br>Events: %{z}<extra></extra>'
    ))
    matrix.update_layout(title='Held-out confusion matrix',
                         xaxis_title='Predicted class',yaxis_title='Actual class',
                         margin={'l':0,'r':0,'t':50,'b':0})
    st.plotly_chart(matrix,use_container_width=True,key='ml_depth_confusion')
    st.caption('Target: shallow/intermediate/deep as defined by recorded depth. '
               'Raw depth and any depth-derived fields were EXCLUDED from model features. '
               'Some reported 10 km depths may be fixed rather than measured.')

    with st.expander('Why we do not show Decision Tree magnitude regression as a main result'):
        r = metrics['decision_tree_regression_experiment']
        st.write(f"Held-out MAE: **{r['test_mae']:.3f}** vs mean-only baseline **{r['baseline_test_mae']:.3f}**; "
                 f"R²: **{r['test_r2']:.3f}**. This model did not improve on the baseline.")
