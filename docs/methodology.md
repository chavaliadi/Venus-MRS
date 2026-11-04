# Methodology

Four stages, matching `src/` one-to-one.

## Stage 1 — Collect data (`src/data_loader.py`)
- Download Magellan images from the NASA PDS (Venus Orbital Data Explorer).
- Record cycle, acquisition date, incidence angle, look direction for every
  image in `data/metadata/observations.csv`.
- Pick one study area (Sif Mons, western flank) and one control area
  (nearby low-relief plains, where no change is expected).

## Stage 2 — Prepare images (`src/preprocessing.py`, `src/speckle_filtering.py`)
- Read the image, mask invalid pixels.
- Remove speckle noise with a 3x3 Lee filter (default) or median filter.
- Put both images on the same grid and align them
  (`src/registration.py`) — ORB feature matching + affine transform.
- **Measure and report the registration RMSE.** This is the floor below
  which no detected change can be trusted.

## Stage 3 — Compare images (`src/change_detection.py`)
- `D = I2 - I1` (difference) and `R = 10 log10(I2 / I1)` (log-ratio, in dB).
- Threshold the result three ways: fixed, Otsu, Kittler–Illingworth
  (the method used in Sulcanese et al. 2024).
- Clean up with morphological opening/closing and drop any region smaller
  than a minimum pixel count.

## Stage 4 — Check results (`src/validation.py`)
- Is the candidate change concentrated on a slope facing the radar?
  → may be viewing geometry, not geology.
- Does the same method flag anything in the control area?
  → that rate is the method's own false-alarm floor.
- Does the candidate survive all three thresholding methods, or does the
  flagged area change a lot between them?

A region that passes all four checks is reported as "possible surface
change." One that fails is reported as "explained by geometry" or
"unclear" — never as confirmed volcanism.

## What's implemented vs. what's next

| Stage | Status |
|---|---|
| Synthetic end-to-end demo (`main.py --demo`) | Working |
| Real Magellan data loader | Written, not yet run on real data |
| Lee / median speckle filters | Working |
| ORB registration + RMSE | Working |
| Difference, log-ratio, Otsu, Kittler–Illingworth | Working |
| Control-region false-alarm check | Working |
| GLCM texture / surface characterization | Not started |
| GB2KI thresholding (Gao et al. 2026) | Future work |
