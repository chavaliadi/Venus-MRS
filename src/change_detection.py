"""
Compare two aligned images and flag candidate change regions.

Implements the two comparison measures and three thresholding methods
named in docs/methodology.md (Week 8–9):
    difference_image, log_ratio
    threshold_fixed, threshold_otsu, threshold_kittler_illingworth
and a cleanup step to remove tiny, almost-certainly-noise regions.
"""
import numpy as np
from scipy import ndimage
from skimage.filters import threshold_otsu as _skimage_otsu
from skimage.measure import label


def difference_image(image_later, image_earlier):
    """D = I2 - I1"""
    return image_later.astype(np.float32) - image_earlier.astype(np.float32)


def log_ratio(image_later, image_earlier, eps=1e-6):
    """R = 10 * log10(I2 / I1), in dB. Both inputs must be positive linear
    backscatter (not already in dB)."""
    a = np.clip(image_earlier, eps, None)
    b = np.clip(image_later, eps, None)
    return 10.0 * np.log10(b / a)


def threshold_fixed(change_map, value):
    """Flag pixels whose absolute change exceeds a fixed value."""
    return np.abs(change_map) > value


def threshold_otsu(change_map):
    """Flag pixels above an automatically chosen Otsu threshold on |change|."""
    magnitude = np.abs(change_map)
    t = _skimage_otsu(magnitude)
    return magnitude > t


def threshold_kittler_illingworth(change_map, n_bins=256):
    """
    Minimum-error (Kittler & Illingworth, 1986) thresholding on |change|.

    This is the method used in Sulcanese et al. (2024). scikit-image does
    not ship it directly, so it's implemented here from the histogram:
    choose the threshold that minimises the overlap cost of fitting two
    Gaussians to the below/above-threshold populations.
    """
    magnitude = np.abs(change_map).ravel()
    hist, bin_edges = np.histogram(magnitude, bins=n_bins)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    hist = hist.astype(np.float64)

    best_t, best_cost = bin_centers[0], np.inf
    total = hist.sum()
    if total == 0:
        return np.zeros_like(change_map, dtype=bool)

    cum = np.cumsum(hist)
    for i in range(1, len(hist) - 1):
        w0, w1 = cum[i], total - cum[i]
        if w0 < 2 or w1 < 2:
            continue
        p0 = hist[: i + 1] / w0
        p1 = hist[i + 1:] / w1
        mu0 = np.sum(bin_centers[: i + 1] * p0)
        mu1 = np.sum(bin_centers[i + 1:] * p1)
        var0 = np.sum(((bin_centers[: i + 1] - mu0) ** 2) * p0) + 1e-6
        var1 = np.sum(((bin_centers[i + 1:] - mu1) ** 2) * p1) + 1e-6

        # Kittler-Illingworth criterion function J(t)
        cost = (
            w0 * np.log(var0) + w1 * np.log(var1)
            - 2 * (w0 * np.log(w0 / total) + w1 * np.log(w1 / total))
        )
        if cost < best_cost:
            best_cost, best_t = cost, bin_centers[i]

    return np.abs(change_map) > best_t


def cleanup_candidate_mask(mask, min_area_px=20):
    """
    Morphological post-processing: binary opening/closing to remove
    speckle-sized flecks, then drop connected components smaller than
    min_area_px. Returns (cleaned_mask, labelled_regions, n_regions).
    """
    opened = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
    closed = ndimage.binary_closing(opened, structure=np.ones((3, 3)))

    labelled = label(closed)
    cleaned = np.zeros_like(closed)
    n_kept = 0
    for region_id in range(1, labelled.max() + 1):
        region = labelled == region_id
        if region.sum() >= min_area_px:
            cleaned |= region
            n_kept += 1

    return cleaned, label(cleaned), n_kept


def area_km2(mask, pixel_spacing_m):
    """Convert a boolean change mask to an area in km^2 given pixel size."""
    n_pixels = int(mask.sum())
    return n_pixels * (pixel_spacing_m ** 2) / 1e6
