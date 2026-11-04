"""
Basic radiometric and housekeeping steps applied before any comparison:
dB conversion, invalid-pixel masking, and simple min-max normalization for
display.
"""
import numpy as np


def to_decibels(image, eps=1e-6):
    """Convert a positive linear backscatter image to a dB scale."""
    safe = np.clip(image, eps, None)
    return 10.0 * np.log10(safe)


def mask_invalid(image, valid_min=0.0, valid_max=None):
    """
    Return a boolean mask of valid pixels (True = usable).

    Masks out non-finite values and anything outside [valid_min, valid_max].
    """
    mask = np.isfinite(image) & (image >= valid_min)
    if valid_max is not None:
        mask &= image <= valid_max
    return mask


def normalize_for_display(image, mask=None):
    """Stretch an image to [0, 1] for plotting (not for analysis)."""
    data = image[mask] if mask is not None else image
    lo, hi = np.percentile(data, [1, 99])
    if hi <= lo:
        hi = lo + 1e-6
    out = np.clip((image - lo) / (hi - lo), 0, 1)
    return out
