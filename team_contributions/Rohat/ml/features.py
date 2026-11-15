"""Reproducible feature construction for the SEISMOSCOPE project.

Input data must be the reviewed USGS 2023-02 to 2024-05 prepared CSV.
Features do not include any event ID or target-derived predictors.
"""
import numpy as np
import pandas as pd


def earth_xyz(df: pd.DataFrame) -> pd.DataFrame:
    """Unit-sphere Cartesian coordinates; avoids discontinuity at ±180° longitude."""
    lat = np.deg2rad(pd.to_numeric(df['latitude'], errors='raise').to_numpy())
    lon = np.deg2rad(pd.to_numeric(df['longitude'], errors='raise').to_numpy())
    return pd.DataFrame({
        'geo_x': np.cos(lat) * np.cos(lon),
        'geo_y': np.cos(lat) * np.sin(lon),
        'geo_z': np.sin(lat),
    }, index=df.index)


def clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """Geography, measured magnitude and log-transformed event depth."""
    x = earth_xyz(df)
    x['magnitude'] = pd.to_numeric(df['mag'], errors='raise').to_numpy()
    x['log_depth_km'] = np.log1p(pd.to_numeric(df['depth'], errors='raise').clip(lower=0)).to_numpy()
    return _validate(x)


def classification_features(df: pd.DataFrame) -> pd.DataFrame:
    """Predict a recorded depth category WITHOUT using depth or any derivative of depth."""
    x = earth_xyz(df)
    x['magnitude'] = pd.to_numeric(df['mag'], errors='raise').to_numpy()
    return _validate(x)


def regression_features(df: pd.DataFrame) -> pd.DataFrame:
    """Exploratory magnitude regression using only event geography/depth."""
    x = earth_xyz(df)
    x['log_depth_km'] = np.log1p(pd.to_numeric(df['depth'], errors='raise').clip(lower=0)).to_numpy()
    return _validate(x)


def _validate(x: pd.DataFrame) -> pd.DataFrame:
    if not np.isfinite(x.to_numpy(dtype=float)).all():
        raise ValueError('Features contain invalid or missing values; verify the prepared input file.')
    return x
