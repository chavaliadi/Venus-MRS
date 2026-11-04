# Venus Surface Characterization using Time-Series Magellan SAR Images

B.Tech project — IIIT Allahabad

**Team:** Siddesh Kishor Rizwani (IEC2023134), Adithya Chavali (IEC2023023)
**Supervisor:** Dr. Himanshu Maurya

## What this project does

NASA's Magellan spacecraft radar-imaged Venus in three separate mapping cycles
(1990–1992), so the same ground was photographed more than once. This project
compares those repeat images to study the surface of Venus, and checks whether
any difference between two images is a real geological change (e.g. a new lava
flow) or just an effect of how the radar looked at the ground (viewing angle,
slope, misalignment, noise).

This repo is the starting codebase: the processing pipeline, structured and
runnable on synthetic data, ready to be pointed at real Magellan images.

## Project structure

```
venus-surface-characterization/
├── src/                    # the actual pipeline, one module per stage
│   ├── data_loader.py      # read images + metadata
│   ├── preprocessing.py    # calibration, masking, dB conversion
│   ├── speckle_filtering.py# Lee / median / Frost filters
│   ├── registration.py     # align two images, report RMSE
│   ├── change_detection.py # difference, log-ratio, thresholding
│   └── validation.py       # control-region + sensitivity checks
├── main.py                 # runs the full pipeline end to end
├── notebooks/               # exploratory Jupyter notebooks (empty for now)
├── data/
│   ├── raw/                 # original downloaded images (not committed)
│   ├── processed/           # filtered/registered outputs (not committed)
│   └── metadata/            # observations.csv — one row per image
├── outputs/
│   ├── figures/             # generated plots
│   └── reports/             # generated tables/summaries
├── docs/
│   ├── literature_review.md
│   └── methodology.md
└── tests/                   # sanity tests for the core math
```

## Status

This is Week 2 of the project. The pipeline below runs end to end on
**synthetic** data to prove the stages connect correctly; it has not yet been
run on real Magellan images. See `docs/methodology.md` for the plan and
`docs/literature_review.md` for the three papers this project builds on.

## Quick start

```bash
pip install -r requirements.txt

# runs the whole pipeline on a synthetic image pair and writes a demo
# figure to outputs/figures/ — no real data needed, just to prove the
# plumbing works
python main.py --demo

# run the sanity tests
pytest tests/
```

Once real Magellan images are downloaded into `data/raw/` and listed in
`data/metadata/observations.csv`, the same `main.py` will run the pipeline on
them instead (see `--help`).

## Data source

[NASA Planetary Data System — Magellan archive](https://pds-geosciences.wustl.edu/missions/magellan/),
searched via the Venus Orbital Data Explorer. See `docs/literature_review.md`
for the published open dataset we are starting from.

## References

1. Sulcanese, D., Mitri, G. & Mastrogiuseppe, M. (2024). *Evidence of ongoing
   volcanic activity on Venus revealed by Magellan radar.* Nature Astronomy
   8, 973–982.
2. Bhiravarasu, S., et al. (2026). *Challenges to detecting present-day
   volcanism on Venus.* Nature Astronomy 10, 485–488.
3. Gao, Y., et al. (2026). *Surface Change Detection on Venus: An
   Inter-Mission Comparison Framework Between Magellan and Future Radar
   Images.* Journal of Geophysical Research: Planets 131(9).
