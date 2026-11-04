"""
Speckle-reduction filters for SAR images.

median_filter and lee_filter are the two used in the project plan (Week 5).
Both default to a 3x3 window, matching docs/methodology.md.
"""
import numpy as np
from scipy.ndimage import median_filter as _median_filter
from scipy.ndimage import uniform_filter


def median_filter(image, size=3):
    """Simple median filter — removes isolated speckle, blurs edges a bit."""
    return _median_filter(image, size=size)


def lee_filter(image, size=3):
    """
    Lee filter: an adaptive speckle filter that smooths flat regions more
    than it smooths edges/textured regions, using local mean and variance.

    Reference: Lee, J.S. (1980), "Digital image enhancement and noise
    filtering by use of local statistics."
    """
    img = image.astype(np.float64)
    mean = uniform_filter(img, size=size)
    sq_mean = uniform_filter(img ** 2, size=size)
    local_var = np.clip(sq_mean - mean ** 2, 0, None)

    overall_var = img.var()
    if overall_var <= 0:
        return img.astype(np.float32)

    weight = local_var / (local_var + overall_var)
    out = mean + weight * (img - mean)
    return out.astype(np.float32)


def equivalent_number_of_looks(image, size=7):
    """
    Estimate the equivalent number of looks (ENL) over a roughly homogeneous
    patch, as (mean / std)^2. Used later to compare filter strength and as
    an input to GB2KI-style thresholding (see docs/methodology.md, future
    work).
    """
    mean = image.mean()
    std = image.std()
    if std == 0:
        return float("inf")
    return float((mean / std) ** 2)
