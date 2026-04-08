# SeqSLAM HQ Bundle

Protocol: `city_village_worlds_hq_rerun_2026-04-07`

## Layout

- `01_seqslam_batch/`: top-level SeqSLAM report, summary table, and requested pair list.
- `02_evo_batch/`: top-level evo report plus filtered sanity and benchmark CSV snapshots for this protocol.
- `03_pairs/<pair>/01_seqslam/`: per-pair SeqSLAM tuning artifacts.
- `03_pairs/<pair>/02_evo/`: per-pair TUM inputs, matched frame export, evo plots, text outputs, and result archives.

## SeqSLAM Pairs

| Pair | Rank | Valid Ratio | Corr | Best Params |
| --- | ---: | ---: | ---: | --- |
| city_summer_vs_city_night | 0.8874 | 0.8626 | 0.8907 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| city_night_vs_city_summer | 0.8214 | 0.9451 | 0.6728 | ds=20, v=(0.80,1.20), R=10, th=1.00 |
| city_night_vs_city_night | 0.9876 | 0.9725 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| city_summer_vs_city_summer | 0.9876 | 0.9725 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| village_summer_vs_village_winter | 0.9097 | 0.9552 | 0.8483 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| village_winter_vs_village_summer | 0.9532 | 0.9552 | 0.9448 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| village_winter_vs_village_winter | 0.9960 | 0.9910 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| village_summer_vs_village_summer | 0.9960 | 0.9910 | 1.0000 | ds=10, v=(0.80,1.20), R=10, th=1.00 |

## Evo Snapshot

| Pair | Mode | APE | RPE Trans | RPE Rot | Eval Poses |
| --- | --- | ---: | ---: | ---: | ---: |
| city_summer_vs_city_night | seqslam_place_match_eval | 56.452329 | 58.875721 | 39.944988 | 314 |
| city_night_vs_city_summer | seqslam_place_match_eval | 113.025033 | 83.274384 | 61.353515 | 344 |
| village_summer_vs_village_winter | seqslam_place_match_eval | 142.494418 | 90.732094 | 32.186772 | 1066 |
| village_winter_vs_village_summer | seqslam_place_match_eval | 95.663280 | 75.319490 | 28.793026 | 1066 |
| city_night_vs_city_night | sanity_selfcheck | 0.000000 | 0.000000 | 0.000000 | 354 |
| city_summer_vs_city_summer | sanity_selfcheck | 0.000000 | 0.000000 | 0.000000 | 354 |
| village_winter_vs_village_winter | sanity_selfcheck | 0.000000 | 0.000000 | 0.000000 | 1106 |
| village_summer_vs_village_summer | sanity_selfcheck | 2.079706 | 1.315917 | 0.000000 | 1106 |