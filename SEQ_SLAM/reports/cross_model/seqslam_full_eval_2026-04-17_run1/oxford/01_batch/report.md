# Oxford SeqSLAM Tuning Bundle

Run label: `2026-04-17_run1`

## Scope

- Front-facing Oxford image path used: `stereo/centre`
- Reference run: `2014-05-14-13-46-12`
- Query runs: self, `2014-06-23-15-36-04`, `2014-06-26-08-53-56`
- Oxford `evo` metrics are available via the post-run extension bundle at `oxford/02_evo_batch/` and per-pair outputs under `oxford/03_pairs/*/02_evo_proxy/`.
- These Oxford evo runs use proxy mode with normalized time alignment for same-route different-speed traversal.

## Best Tuning Rows

| Pair | Rank | Valid Ratio | Corr | Norm MAE | Best Params |
| --- | ---: | ---: | ---: | ---: | --- |
| 2014-05-14-13-46-12_vs_2014-05-14-13-46-12 | 0.9975 | 0.9966 | 0.9979 | 0.0008 | ds=10, v=(0.80,1.20), R=10, th=1.00 |
| 2014-05-14-13-46-12_vs_2014-06-23-15-36-04 | 0.8113 | 0.9855 | 0.5982 | 0.1427 | ds=50, v=(0.50,1.50), R=10, th=1.00 |
| 2014-05-14-13-46-12_vs_2014-06-26-08-53-56 | 0.8123 | 0.9836 | 0.6013 | 0.1384 | ds=50, v=(0.80,1.20), R=10, th=1.00 |

## Artifact Index

- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-05-14-13-46-12/01_seqslam/tuning_summary.csv`
- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-05-14-13-46-12/01_seqslam/oxford_tuning_best_matchings.png`
- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-23-15-36-04/01_seqslam/tuning_summary.csv`
- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-23-15-36-04/01_seqslam/oxford_tuning_best_matchings.png`
- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-26-08-53-56/01_seqslam/tuning_summary.csv`
- `oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-26-08-53-56/01_seqslam/oxford_tuning_best_matchings.png`