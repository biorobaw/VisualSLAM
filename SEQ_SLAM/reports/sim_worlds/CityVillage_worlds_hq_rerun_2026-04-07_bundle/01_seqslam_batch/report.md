# City/Village Simulator Tuning Report

This is a separate evaluation track from Oxford.

Protocol: **city_village_worlds_hq_rerun_2026-04-07**

## Evaluated comparisons
- city: city_summer vs city_night
- city: city_night vs city_summer
- city: city_night vs city_night
- city: city_summer vs city_summer
- village: village_summer vs village_winter
- village: village_winter vs village_summer
- village: village_winter vs village_winter
- village: village_summer vs village_summer

## Command
```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py --pairs-csv ../reports/sim_worlds/CityVillage_worlds/requested_pairs_hq_2026-04-07.csv --protocol-label city_village_worlds_hq_rerun_2026-04-07 --report-subdir CityVillage_worlds_hq_rerun_2026-04-07 --auto-query-stride --no-cache
```

## Outcome
- Tunings passed: **8/8**

## Per-pair best tuning summary

| Dataset | Reference | Query | Pass | Rank | Valid Ratio | Corr | Norm MAE | Best Params |
|---|---|---|---:|---:|---:|---:|---:|---|
| city | city_summer | city_night | True | 0.8874 | 0.8626 | 0.8907 | 0.0471 | ds=50, v=(0.80,1.20), R=10, th=1.00, gate=True |
| city | city_night | city_summer | True | 0.8214 | 0.9451 | 0.6728 | 0.1531 | ds=20, v=(0.80,1.20), R=10, th=1.00, gate=True |
| city | city_night | city_night | True | 0.9876 | 0.9725 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80, gate=True |
| city | city_summer | city_summer | True | 0.9876 | 0.9725 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80, gate=True |
| village | village_summer | village_winter | True | 0.9097 | 0.9552 | 0.8483 | 0.0628 | ds=50, v=(0.80,1.20), R=10, th=1.00, gate=True |
| village | village_winter | village_summer | True | 0.9532 | 0.9552 | 0.9448 | 0.0300 | ds=50, v=(0.80,1.20), R=10, th=1.00, gate=True |
| village | village_winter | village_winter | True | 0.9960 | 0.9910 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80, gate=True |
| village | village_summer | village_summer | True | 0.9960 | 0.9910 | 1.0000 | 0.0001 | ds=10, v=(0.80,1.20), R=10, th=1.00, gate=True |

## Artifact index
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_night/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_night/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_night_vs_city_summer/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_night_vs_city_summer/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_night_vs_city_night/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_night_vs_city_night/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_summer/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_summer/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_winter/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_winter/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_winter_vs_village_summer/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_winter_vs_village_summer/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_winter_vs_village_winter/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_winter_vs_village_winter/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_summer/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_summer/sim_worlds_tuning_best_matchings.png
