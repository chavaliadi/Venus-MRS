import numpy as np

from src import change_detection as cd


def test_difference_image_is_zero_for_identical_inputs():
    img = np.random.rand(10, 10).astype(np.float32)
    diff = cd.difference_image(img, img)
    assert np.allclose(diff, 0)


def test_log_ratio_is_zero_for_identical_inputs():
    img = np.random.rand(10, 10).astype(np.float32) + 0.1
    ratio = cd.log_ratio(img, img)
    assert np.allclose(ratio, 0, atol=1e-5)


def test_threshold_fixed_flags_only_large_changes():
    change = np.zeros((5, 5), dtype=np.float32)
    change[2, 2] = 10.0
    mask = cd.threshold_fixed(change, value=1.0)
    assert mask.sum() == 1
    assert mask[2, 2]


def test_cleanup_removes_single_pixel_noise():
    mask = np.zeros((20, 20), dtype=bool)
    mask[5, 5] = True  # single isolated pixel: should be removed
    mask[10:15, 10:15] = True  # a real 5x5 blob: should survive
    cleaned, _, n_regions = cd.cleanup_candidate_mask(mask, min_area_px=5)
    assert not cleaned[5, 5]
    assert cleaned[12, 12]
    assert n_regions == 1


def test_area_km2_matches_pixel_count():
    mask = np.zeros((10, 10), dtype=bool)
    mask[:2, :2] = True  # 4 pixels
    area = cd.area_km2(mask, pixel_spacing_m=1000.0)  # 1 km per pixel
    assert np.isclose(area, 4.0)
