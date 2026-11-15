"""Train/evaluate K-Means and Decision Tree models for CEN445 SEISMOSCOPE.

Run from project root: python -m ml.train_models
Only reviewed historical catalog records are analyzed. No forecast of future
seismic activity, hazard, or aftershock probability is performed.
"""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score, mean_absolute_error, mean_squared_error,
    r2_score, silhouette_score,
)
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from .features import classification_features, clustering_features, regression_features

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'earthquakes_dashboard_ready.csv'
OUT = ROOT / 'ml'
MODELS = OUT / 'models'
REPORTS = OUT / 'reports'
RANDOM_STATE = 42


def native(v):
    """JSON conversion of numpy scalars and arrays."""
    if isinstance(v, dict):
        return {str(k): native(w) for k, w in v.items()}
    if isinstance(v, (list, tuple)):
        return [native(w) for w in v]
    if isinstance(v, np.ndarray):
        return native(v.tolist())
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v


def main():
    MODELS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DATA, low_memory=False)
    if not 2000 <= len(d) <= 10000 or d.shape[1] < 7:
        raise ValueError(f'Dataset does not meet project size requirements: {d.shape}')
    if not d['id'].is_unique or not d['type'].eq('earthquake').all():
        raise ValueError('Duplicate IDs or unexpected event types in dataset')
    d['timestamp'] = pd.to_datetime(d['time'], utc=True, errors='raise')
    d = d.sort_values(['timestamp','id']).reset_index(drop=True)
    # Strict chronological holdout. Model selection is done only on the earlier period.
    cut = int(len(d) * 0.8)
    train, test = d.iloc[:cut], d.iloc[cut:]
    info = {
        'dataset_rows': len(d), 'dataset_columns': 34,
        'date_min_utc': str(d['timestamp'].iloc[0]),
        'date_max_utc': str(d['timestamp'].iloc[-1]),
        'train_rows': len(train), 'test_rows': len(test),
        'test_period_start_utc': str(test['timestamp'].iloc[0]),
        'split_method': 'Chronological 80% training / 20% held-out test',
        'seed': RANDOM_STATE,
    }

    # ------------------- K-means: unsupervised, ALL catalog events -------------
    clustering_x = clustering_features(d)
    # Silhouette is evaluated on the SAME deterministic random subsample across k.
    # Only k selection uses labels; no human-assigned reference targets exist.
    scores = {}
    kmodels = {}
    subsample_idx = np.random.default_rng(RANDOM_STATE).choice(len(d), size=min(1500, len(d)), replace=False)
    for k in range(3, 8):
        p = Pipeline([
            ('scale', StandardScaler()),
            ('cluster', KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)),
        ])
        labels = p.fit_predict(clustering_x)
        counts = np.bincount(labels, minlength=k)
        score = silhouette_score(p.named_steps['scale'].transform(clustering_x.iloc[subsample_idx]),
                                 labels[subsample_idx])
        scores[str(k)] = {'silhouette_sample': float(score),
                          'smallest_cluster_rows': int(counts.min()),
                          'smallest_cluster_fraction': float(counts.min()/len(d))}
        kmodels[k] = p
    # Avoid a model whose smallest cluster has <1% of the total data.
    eligible = [int(k) for k,v in scores.items() if v['smallest_cluster_fraction'] >= 0.01]
    if not eligible:
        eligible = list(kmodels)
    selected_k = max(eligible, key=lambda k: scores[str(k)]['silhouette_sample'])
    cluster_model = kmodels[selected_k]
    cluster_labels = cluster_model.predict(clustering_x)
    joblib.dump(cluster_model, MODELS / 'kmeans_pipeline.joblib')
    cluster_profiles = d.assign(cluster=cluster_labels).groupby('cluster').agg(
        count=('id','size'), avg_mag=('mag','mean'), median_depth_km=('depth','median'),
        avg_depth_km=('depth','mean'), north_fraction=('latitude',lambda x:float((x>=0).mean()))
    ).reset_index()
    cluster_profiles['share_pct'] = (100*cluster_profiles['count']/len(d)).round(2)
    cluster_profiles.to_csv(REPORTS / 'cluster_profiles.csv', index=False)
    kmeans_result = {'selected_k':selected_k,'silhouette_search':scores,
                     'features':list(clustering_x.columns),
                     'model_fit_rows':len(d),
                     'cluster_counts':dict(zip(map(str,range(selected_k)),
                                            np.bincount(cluster_labels,minlength=selected_k).tolist()))}

    # ------------------- Decision Tree CLASSIFICATION -------------------------
    # Targets are depth labels; NEVER input depth, 10km flag or depth_category.
    c_x = classification_features(d)
    c_y = d['depth_category']
    cv = TimeSeriesSplit(n_splits=4)
    classifier_search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=RANDOM_STATE, class_weight='balanced'),
        param_grid={'max_depth': [4,5,6,8,10], 'min_samples_leaf': [20,50,100]},
        scoring='balanced_accuracy', cv=cv, n_jobs=1, refit=True,
    )
    classifier_search.fit(c_x.iloc[:cut],c_y.iloc[:cut])
    clf = classifier_search.best_estimator_
    c_pred = clf.predict(c_x.iloc[cut:])
    classes = list(clf.classes_)
    cbaseline = DummyClassifier(strategy='most_frequent')
    cbaseline.fit(c_x.iloc[:cut],c_y.iloc[:cut])
    base_pred = cbaseline.predict(c_x.iloc[cut:])
    classifier_result = {
        'features':list(c_x.columns),
        'target':'depth_category (cataloged shallow/intermediate/deep)',
        'best_params':classifier_search.best_params_,
        'crossval_train_balanced_accuracy':float(classifier_search.best_score_),
        'test_accuracy':float(accuracy_score(c_y.iloc[cut:],c_pred)),
        'test_balanced_accuracy':float(balanced_accuracy_score(c_y.iloc[cut:],c_pred)),
        'test_macro_f1':float(f1_score(c_y.iloc[cut:],c_pred,average='macro')),
        'test_weighted_f1':float(f1_score(c_y.iloc[cut:],c_pred,average='weighted')),
        'baseline_majority_test_accuracy':float(accuracy_score(c_y.iloc[cut:],base_pred)),
        'baseline_majority_test_balanced_accuracy':float(balanced_accuracy_score(c_y.iloc[cut:],base_pred)),
        'baseline_majority_test_macro_f1':float(f1_score(c_y.iloc[cut:],base_pred,average='macro')),
        'classes': classes,
        'confusion_matrix_rows_actual_cols_predicted': confusion_matrix(c_y.iloc[cut:],c_pred,labels=classes),
        'per_class_report':classification_report(c_y.iloc[cut:],c_pred,labels=classes,output_dict=True,zero_division=0),
    }
    joblib.dump(clf, MODELS / 'decision_tree_classifier.joblib')

    # ------------------- Decision Tree REGRESSION (candidate) ------------------
    # Diagnostic to assess the previously suggested task. A weak result should
    # not be presented as if earthquake magnitude were predictable this way.
    r_x = regression_features(d)
    r_y = d['mag']
    regression_search = GridSearchCV(
        estimator=DecisionTreeRegressor(random_state=RANDOM_STATE),
        param_grid={'max_depth':[2,3,4,5,6], 'min_samples_leaf':[20,50,100,200]},
        scoring='neg_mean_absolute_error', cv=cv, n_jobs=1, refit=True,
    )
    regression_search.fit(r_x.iloc[:cut],r_y.iloc[:cut])
    reg = regression_search.best_estimator_
    r_pred = reg.predict(r_x.iloc[cut:])
    base = DummyRegressor(strategy='mean').fit(r_x.iloc[:cut],r_y.iloc[:cut])
    base_r_pred = base.predict(r_x.iloc[cut:])
    mae = float(mean_absolute_error(r_y.iloc[cut:],r_pred))
    baseline_mae = float(mean_absolute_error(r_y.iloc[cut:],base_r_pred))
    regression_result = {
        'features':list(r_x.columns), 'target':'mag (recorded earthquake magnitude)',
        'best_params':regression_search.best_params_,
        'train_cv_mae':float(-regression_search.best_score_),
        'test_mae':mae,'test_rmse':float(np.sqrt(mean_squared_error(r_y.iloc[cut:],r_pred))),
        'test_r2':float(r2_score(r_y.iloc[cut:],r_pred)),
        'baseline_train_mean_magnitude':float(r_y.iloc[:cut].mean()),
        'baseline_test_mae':baseline_mae,
        'improvement_over_dummy_mae_pct':float(100 * (baseline_mae - mae)/baseline_mae),
        'recommended_for_dashboard':bool(mae < baseline_mae * .95),
    }
    joblib.dump(reg, MODELS / 'decision_tree_regressor_experimental.joblib')

    # Assign scores by event ID; no assumptions about input file ordering.
    output = d[['id','time','latitude','longitude','depth','mag','depth_category']].copy()
    output['kmeans_cluster'] = cluster_labels
    output['chronological_split'] = np.where(np.arange(len(d))<cut,'train','test')
    output['depth_category_model_prediction'] = pd.Series(dtype='object')
    output['magnitude_model_prediction'] = np.nan
    output.loc[output.index[cut:],'depth_category_model_prediction'] = c_pred
    output.loc[output.index[cut:],'magnitude_model_prediction'] = r_pred
    output.to_csv(REPORTS / 'ml_scored_events.csv',index=False)

    metrics = native({'dataset':info,'kmeans':kmeans_result,
                      'decision_tree_classification':classifier_result,
                      'decision_tree_regression_experiment':regression_result})
    (REPORTS/'metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Training finished.\n')
    print('Dataset:',info)
    print('KMeans k:',selected_k, 'silhouette:',round(scores[str(selected_k)]['silhouette_sample'],4))
    print('Classification best params:',classifier_result['best_params'])
    print('Classification test balanced accuracy:',round(classifier_result['test_balanced_accuracy'],4))
    print('Classification test macro F1:',round(classifier_result['test_macro_f1'],4))
    print('Regression test MAE / dummy MAE:',round(mae,4),'/',round(baseline_mae,4))
    print('Regression test R²:',round(regression_result['test_r2'],4))
    print('Artifacts in:',ROOT)

if __name__ == '__main__':
    main()
