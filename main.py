#!/usr/bin/env python3
"""
Venus Surface Characterization — pipeline entry point.

Usage:
    python main.py --demo
        Runs the full pipeline on a synthetic image pair (no real data
        needed) and writes outputs/figures/demo_change_map.png. This is
        here to prove the stages connect correctly before real Magellan
        data is downloaded.

    python main.py --metadata data/metadata/observations.csv \\
                    --cycle-a 1 --cycle-b 3 --region "Sif Mons"
        Runs the pipeline on a real registered image pair once
        data/metadata/observations.csv has matching entries.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src import data_loader, preprocessing, speckle_filtering
from src import registration, change_detection, validation

FIGURES_DIR = Path("outputs/figures")


def run_pipeline(image_1, image_2, pixel_spacing_m=75.0, label="demo"):
    """Stage 2-4 of docs/methodology.md, given two raw-ish images."""

    # --- Stage 2: prepare -------------------------------------------------
    filtered_1 = speckle_filtering.lee_filter(image_1)
    filtered_2 = speckle_filtering.lee_filter(image_2)

    aligned_2, rmse_px, n_matches = registration.register_images(
        filtered_1, filtered_2
    )
    print(f"[{label}] registration: RMSE = {rmse_px:.3f} px "
          f"({n_matches} tie points)")

    # --- Stage 3: compare ---------------------------------------------------
    diff = change_detection.difference_image(aligned_2, filtered_1)
    ratio_db = change_detection.log_ratio(
        np.clip(aligned_2, 1e-3, None), np.clip(filtered_1, 1e-3, None)
    )

    mask_otsu = change_detection.threshold_otsu(diff)
    mask_ki = change_detection.threshold_kittler_illingworth(diff)
    agreed = validation.agreement_mask(mask_otsu, mask_ki)
    cleaned, _, n_regions = change_detection.cleanup_candidate_mask(agreed)
    area = change_detection.area_km2(cleaned, pixel_spacing_m)

    print(f"[{label}] candidate regions after cleanup: {n_regions} "
          f"(~{area:.2f} km^2 at {pixel_spacing_m} m/pixel)")

    sensitivity = validation.threshold_sensitivity(diff)
    print(f"[{label}] threshold sensitivity (flagged fraction): "
          f"{sensitivity}")

    return {
        "filtered_1": filtered_1,
        "aligned_2": aligned_2,
        "diff": diff,
        "ratio_db": ratio_db,
        "candidate_mask": cleaned,
        "rmse_px": rmse_px,
        "n_regions": n_regions,
        "area_km2": area,
        "sensitivity": sensitivity,
    }


def save_summary_figure(image_1, image_2, result, out_path):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.2))

    axes[0].imshow(image_1, cmap="gray")
    axes[0].set_title("Image 1 (earlier)")

    axes[1].imshow(result["aligned_2"], cmap="gray")
    axes[1].set_title("Image 2 (later, aligned)")

    axes[2].imshow(result["diff"], cmap="RdBu_r")
    axes[2].set_title("Difference  D = I2 - I1")

    axes[3].imshow(image_1, cmap="gray")
    axes[3].imshow(
        np.ma.masked_where(~result["candidate_mask"], result["candidate_mask"]),
        cmap="autumn", alpha=0.6,
    )
    axes[3].set_title(f"Candidate change\n({result['n_regions']} region(s), "
                       f"{result['area_km2']:.2f} km²)")

    for ax in axes:
        ax.axis("off")

    fig.suptitle(
        f"Registration RMSE: {result['rmse_px']:.2f} px   |   "
        f"demo run on synthetic data",
        fontsize=10,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                         help="run on a synthetic image pair")
    parser.add_argument("--metadata", type=str, default=None,
                         help="path to data/metadata/observations.csv")
    parser.add_argument("--cycle-a", type=int, default=1)
    parser.add_argument("--cycle-b", type=int, default=3)
    parser.add_argument("--region", type=str, default=None)
    args = parser.parse_args()

    if args.demo or args.metadata is None:
        print("Running in demo mode on a synthetic image pair "
              "(no real Magellan data required).\n")
        image_1, image_2 = data_loader.make_synthetic_pair()
        result = run_pipeline(image_1, image_2, label="demo")
        save_summary_figure(
            image_1, image_2, result, FIGURES_DIR / "demo_change_map.png"
        )
        return

    meta = data_loader.load_metadata(args.metadata)
    row_a, row_b = data_loader.find_pair(
        meta, args.cycle_a, args.cycle_b, region=args.region
    )
    image_1 = data_loader.load_image(row_a["path"])
    image_2 = data_loader.load_image(row_b["path"])
    pixel_spacing = float(row_a.get("pixel_spacing_m", 75.0))

    result = run_pipeline(
        image_1, image_2, pixel_spacing_m=pixel_spacing,
        label=args.region or "real",
    )
    out_name = f"change_map_{(args.region or 'region').replace(' ', '_')}.png"
    save_summary_figure(image_1, image_2, result, FIGURES_DIR / out_name)


if __name__ == "__main__":
    main()
