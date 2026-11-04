# Literature Review

| # | Publication | What it did | Takeaway for this project |
|---|---|---|---|
| 1 | Sulcanese, Mitri & Mastrogiuseppe (2024), *Evidence of ongoing volcanic activity on Venus revealed by Magellan radar*, Nature Astronomy 8, 973–982. DOI: 10.1038/s41550-024-02272-1 | Compared Cycle 1 vs Cycle 3 backscatter at Sif Mons and Niobe Planitia; Kittler–Illingworth thresholding on the difference. Found ~30 km² and ~45 km² of candidate new lava flows. | Direct analogue of our pipeline. Their processed images are openly released — our starting point. Gap: no reported registration error, no control region. |
| 2 | Bhiravarasu et al. (2026), *Challenges to detecting present-day volcanism on Venus*, Nature Astronomy 10, 485–488. DOI: 10.1038/s41550-026-02832-7 | Re-examined the same anomalies; showed the backscatter differences are consistent with the change in viewing geometry between cycles. | The critique our validation stage answers directly. |
| 3 | Gao et al. (2026), *Surface Change Detection on Venus: An Inter-Mission Comparison Framework*, J. Geophys. Res. Planets 131(9). DOI: 10.1029/2026JE009994 | GB2KI — generalized beta-prime distribution inside Kittler–Illingworth thresholding, for image pairs with unequal equivalent number of looks. | Confirms thresholding is the weak link. Realistic extension once the baseline pipeline runs on real data. |

See the presentation decks for the fuller survey.
