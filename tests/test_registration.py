import numpy as np

from src import data_loader, registration


def test_register_identical_images_has_near_zero_rmse():
    image_1, _ = data_loader.make_synthetic_pair(size=200, seed=1)
    aligned, rmse_px, n_matches = registration.register_images(image_1, image_1)
    assert n_matches > 0
    assert rmse_px < 1.0  # registering an image to itself should be ~perfect
