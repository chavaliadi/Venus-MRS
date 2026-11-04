"""
Align two images of the same region taken at different times, and report
how accurate that alignment is (RMSE of matched tie points).

Uses ORB feature matching + an estimated affine transform (OpenCV). This is
the method named in docs/methodology.md for Week 6.
"""
import cv2
import numpy as np


def _to_uint8(image):
    norm = (image - image.min()) / (np.ptp(image) + 1e-9)
    return (norm * 255).astype(np.uint8)


def register_images(reference, moving, max_features=500, good_match_pct=0.5):
    """
    Register `moving` onto `reference` using ORB keypoints + affine fit.

    Returns:
        aligned      — `moving` warped into `reference`'s coordinate frame
        rmse_pixels  — root-mean-square residual of the matched tie points
        n_matches    — number of tie points used for the fit
    """
    ref8 = _to_uint8(reference)
    mov8 = _to_uint8(moving)

    orb = cv2.ORB_create(max_features)
    kp1, des1 = orb.detectAndCompute(ref8, None)
    kp2, des2 = orb.detectAndCompute(mov8, None)

    if des1 is None or des2 is None or len(kp1) < 3 or len(kp2) < 3:
        raise RuntimeError(
            "Not enough features found to register these images — "
            "try a larger subscene or check the images aren't blank."
        )

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = sorted(matcher.match(des1, des2), key=lambda m: m.distance)
    n_good = max(3, int(len(matches) * good_match_pct))
    good = matches[:n_good]

    pts_ref = np.float32([kp1[m.queryIdx].pt for m in good])
    pts_mov = np.float32([kp2[m.trainIdx].pt for m in good])

    transform, inliers = cv2.estimateAffinePartial2D(pts_mov, pts_ref)
    if transform is None:
        raise RuntimeError("Could not estimate a registration transform.")

    h, w = reference.shape
    aligned = cv2.warpAffine(moving, transform, (w, h))

    # RMSE of the inlier tie points after applying the fitted transform
    inlier_mask = inliers.ravel().astype(bool)
    src = pts_mov[inlier_mask]
    dst = pts_ref[inlier_mask]
    ones = np.ones((src.shape[0], 1), dtype=np.float32)
    src_h = np.hstack([src, ones])
    predicted = src_h @ transform.T
    residuals = predicted - dst
    rmse_pixels = float(np.sqrt(np.mean(np.sum(residuals ** 2, axis=1))))

    return aligned, rmse_pixels, int(inlier_mask.sum())
