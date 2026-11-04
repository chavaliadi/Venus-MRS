"""
Load Magellan SAR images and their metadata.

Real Magellan products (GeoTIFF, PDS IMG) are read with rasterio. That
import is kept lazy (inside the function, not at module load time) so the
rest of the pipeline can be developed and tested on synthetic arrays before
rasterio or real data is available.
"""
from pathlib import Path

import numpy as np
import pandas as pd


def load_image(path):
    """
    Read a single-band radar image from disk into a float32 numpy array.

    Supports GeoTIFF / any format rasterio can read. Values are returned
    as-is (not yet calibrated — see preprocessing.to_decibels).
    """
    import rasterio  # lazy import, see module docstring

    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
    return arr


def load_metadata(csv_path):
    """
    Load the observations table (one row per downloaded image).

    Expected columns: image_id, cycle, acquisition_date, lat, lon,
    incidence_angle, look_direction, pixel_spacing_m, calibrated, path
    """
    return pd.read_csv(csv_path)


def find_pair(metadata_df, cycle_a, cycle_b, region=None):
    """
    Pick one image from cycle_a and one from cycle_b for a given region.

    Returns a (row_a, row_b) tuple of pandas Series, or raises ValueError
    if a matching pair isn't in the metadata table yet.
    """
    df = metadata_df
    if region is not None and "region" in df.columns:
        df = df[df["region"] == region]

    rows_a = df[df["cycle"] == cycle_a]
    rows_b = df[df["cycle"] == cycle_b]
    if rows_a.empty or rows_b.empty:
        raise ValueError(
            f"No image pair found for cycles {cycle_a}/{cycle_b}"
            f"{' in region ' + region if region else ''}. "
            "Add entries to data/metadata/observations.csv first."
        )
    return rows_a.iloc[0], rows_b.iloc[0]


def make_synthetic_pair(size=256, seed=0):
    """
    Generate a synthetic "before/after" SAR-like image pair for testing the
    pipeline end to end before real Magellan data is downloaded.

    Returns (image_1, image_2) as float32 arrays in roughly [0, 1], with a
    bright rectangular patch injected into image_2 to simulate a candidate
    change region.
    """
    rng = np.random.default_rng(seed)

    base = rng.gamma(shape=4.0, scale=0.1, size=(size, size)).astype(np.float32)
    base = np.clip(base, 0, 1)

    image_1 = base.copy()
    image_2 = base.copy()

    # inject a synthetic "new lava flow" — a bright patch — into image_2
    y0, y1 = int(size * 0.55), int(size * 0.68)
    x0, x1 = int(size * 0.30), int(size * 0.55)
    image_2[y0:y1, x0:x1] += rng.uniform(0.35, 0.55)
    image_2 = np.clip(image_2, 0, 1)

    return image_1, image_2
