# SeqSLAM HQ Bundle

Protocol: `seqslam_full_eval_2026-04-17_run1_sim_worlds`

## Layout

- `01_seqslam_batch/`: top-level SeqSLAM report, summary table, and requested pair list.
- `02_evo_batch/`: top-level evo report plus filtered sanity and benchmark CSV snapshots for this protocol.
- `03_pairs/<pair>/01_seqslam/`: per-pair SeqSLAM tuning artifacts.
- `03_pairs/<pair>/02_evo/`: per-pair TUM inputs, matched frame export, evo plots, text outputs, and result archives.

## SeqSLAM Pairs

| Pair | Rank | Valid Ratio | Corr | Best Params |
| --- | ---: | ---: | ---: | --- |
| city_summer_vs_city_summer | 0.9876 | 0.9725 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| city_summer_vs_city_night | 0.6610 | 0.8626 | 0.3747 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| village_summer_vs_village_summer | 0.9960 | 0.9910 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=0.90 |
| village_summer_vs_village_winter | 0.8754 | 0.9552 | 0.7726 | ds=50, v=(0.80,1.20), R=10, th=1.00 |

## Evo Snapshot

| Pair | Mode | APE | RPE Trans | RPE Rot | Eval Poses |
| --- | --- | ---: | ---: | ---: | ---: |
| city_summer_vs_city_night | seqslam_place_match_eval | 117.554348 | 111.762542 | 85.050226 | 314 |
| village_summer_vs_village_winter | seqslam_place_match_eval | 173.794906 | 152.112170 | 51.437498 | 1066 |
| city_summer_vs_city_summer | sanity_selfcheck | 0.000000 | 0.000000 | 0.000000 | 354 |
| village_summer_vs_village_summer | sanity_selfcheck | 0.000000 | 0.000000 | 0.000000 | 1106 |