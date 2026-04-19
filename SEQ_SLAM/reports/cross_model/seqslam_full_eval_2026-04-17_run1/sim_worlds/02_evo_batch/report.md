# SeqSLAM Sim-World Match Evaluation

Date: 2026-04-17

## Scope

- Source tuning summary: `SEQ_SLAM/reports/sim_worlds/SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning/summary.csv`
- Camera subdirectory(s): `mono_front`
- For each pair, recompute the best-match sequence from SeqSLAM using the selected tuning row.
- Export GT query poses and matched reference poses into synchronized TUM trajectories on valid matched frames only.
- Run raw `evo` translation/rotation metrics without alignment because the simulator trajectories already share a coordinate frame.

## Results

| Sequence | Valid Ratio | Corr | Eval Poses | APE XY RMSE | RPE XY RMSE | RPE Rot RMSE | Pair Dir |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| city_summer_vs_city_summer | 0.9725 | 1.0000 | 354 | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer` |
| city_summer_vs_city_night | 0.8626 | 0.3747 | 314 | 117.554348 | 111.762542 | 85.050226 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night` |
| village_summer_vs_village_summer | 0.9910 | 1.0000 | 1106 | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer` |
| village_summer_vs_village_winter | 0.9552 | 0.7726 | 1066 | 173.794906 | 152.112170 | 51.437498 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter` |

## Artifact Index

- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/inputs/city_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/inputs/city_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_summer/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/inputs/city_night_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/inputs/city_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/city_summer_vs_city_night/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/inputs/village_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/inputs/village_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_summer/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/inputs/village_winter_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/inputs/village_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/village_summer_vs_village_winter/outputs/rpe_rot_raw.pdf`