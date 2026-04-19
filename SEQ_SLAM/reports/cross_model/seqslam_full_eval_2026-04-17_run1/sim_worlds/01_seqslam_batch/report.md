# City/Village Simulator Tuning Report

This is a separate evaluation track from Oxford.

Protocol: **seqslam_full_eval_2026-04-17_run1_sim_worlds**

## Evaluated comparisons
- city: city_summer vs city_summer (camera: mono_front)
- city: city_summer vs city_night (camera: mono_front)
- village: village_summer vs village_summer (camera: mono_front)
- village: village_summer vs village_winter (camera: mono_front)

## Command
```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py --pairs-csv /Users/asadbeknematov/Desktop/Projects/VisualSLAM/SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/inputs/sim_world_pairs.csv --protocol-label seqslam_full_eval_2026-04-17_run1_sim_worlds --report-subdir SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning --camera-subdir mono_front --result-tag seqslam_full_eval_2026-04-17_run1 --auto-query-stride --no-cache
```

## Outcome
- Tunings passed: **4/4**

## Per-pair best tuning summary

| Dataset | Reference | Query | Pass | Rank | Valid Ratio | Corr | Norm MAE | Best Params |
|---|---|---|---:|---:|---:|---:|---:|---|
| city | city_summer | city_summer | True | 0.9876 | 0.9725 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80, gate=True |
| city | city_summer | city_night | True | 0.6610 | 0.8626 | 0.3747 | 0.1803 | ds=50, v=(0.80,1.20), R=10, th=1.00, gate=True |
| village | village_summer | village_summer | True | 0.9960 | 0.9910 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.90, gate=True |
| village | village_summer | village_winter | True | 0.8754 | 0.9552 | 0.7726 | 0.0896 | ds=50, v=(0.80,1.20), R=10, th=1.00, gate=True |

## Artifact index
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_summer_seqslam_full_eval_2026-04-17_run1/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_summer_seqslam_full_eval_2026-04-17_run1/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_night_seqslam_full_eval_2026-04-17_run1/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city/city_city_summer_vs_city_night_seqslam_full_eval_2026-04-17_run1/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_summer_seqslam_full_eval_2026-04-17_run1/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_summer_seqslam_full_eval_2026-04-17_run1/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_winter_seqslam_full_eval_2026-04-17_run1/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village/village_village_summer_vs_village_winter_seqslam_full_eval_2026-04-17_run1/sim_worlds_tuning_best_matchings.png
