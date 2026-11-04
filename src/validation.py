"""
Checks that turn a raw candidate-change mask into a trustworthy result:
a control-region false-alarm rate, and a threshold-sensitivity sweep.

These are the checks from docs/methodology.md (Week 10) and the
Validation Strategy slide of Presentation 1.
"""
import numpy as np

from src.change_detection import (
    threshold_fixed,
    threshold_otsu,
    threshold_kittler_illingworth,
    cleanup_candidate_mask,
)


def false_alarm_rate(control_change_map, min_area_px=20):
    """
    Run the same cleanup used on the study area over a control region
    (where no real change is expected) and report what fraction of it
    still gets flagged — this is the method's own noise floor.
    """
    mask = threshold_otsu(control_change_map)
    cleaned, _, _ = cleanup_candidate_mask(mask, min_area_px=min_area_px)
    return float(cleaned.mean())  # fraction of pixels flagged


def threshold_sensitivity(change_map, fixed_value=None):
    """
    Compare the flagged fraction of the image under all three thresholding
    methods. A result that moves a great deal between methods is not a
    reliable detection (see Validation Strategy).

    Returns a dict: {"fixed": frac, "otsu": frac, "kittler_illingworth": frac}
    """
    out = {}
    if fixed_value is not None:
        out["fixed"] = float(threshold_fixed(change_map, fixed_value).mean())
    out["otsu"] = float(threshold_otsu(change_map).mean())
    out["kittler_illingworth"] = float(
        threshold_kittler_illingworth(change_map).mean()
    )
    return out


def agreement_mask(*masks):
    """Pixels flagged by every method given — the conservative, trusted set."""
    stacked = np.stack(masks)
    return np.all(stacked, axis=0)
