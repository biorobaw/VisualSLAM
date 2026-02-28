# City/Village Simulator Tuning Report

This is a separate evaluation phase from Oxford (not Phase 2).

## Evaluated comparisons
- city day vs city day
- city day vs city night
- village day vs village day
- village day vs village winter

## Command
```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py --auto-query-stride --no-cache
```

## Outcome
- Tunings passed: **4/4**

## Per-pair best tuning summary

| Dataset | Reference | Query | Pass | Rank | Valid Ratio | Corr | Norm MAE | Best Params |
|---|---|---|---:|---:|---:|---:|---:|---|
| city_sim | city_sim_day_centerline | city_sim_day_centerline | True | 0.9876 | 0.9725 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| city_sim | city_sim_day_centerline | city_sim_night_centerline | True | 0.8130 | 0.8626 | 0.7319 | 0.1193 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| village_sim | village_sim_day_centerline_smooth | village_sim_day_centerline_smooth | True | 0.9960 | 0.9910 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=1.00 |
| village_sim | village_sim_day_centerline_smooth | village_sim_winter_centerline_smooth | True | 0.9611 | 0.9552 | 0.9609 | 0.0210 | ds=50, v=(0.80,1.20), R=10, th=1.00 |

## Artifact index
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_day_centerline/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_day_centerline/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_night_centerline/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_night_centerline/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_day_centerline_smooth/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_day_centerline_smooth/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth/sim_worlds_tuning_best_matchings.png
