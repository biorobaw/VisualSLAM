# SeqSLAM Sim-World Match Evaluation

Date: 2026-04-07

## Scope

- Source tuning summary: `SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_hq_rerun_2026-04-07/summary.csv`
- For each pair, recompute the best-match sequence from SeqSLAM using the selected tuning row.
- Export GT query poses and matched reference poses into synchronized TUM trajectories on valid matched frames only.
- Run raw `evo` translation/rotation metrics without alignment because the simulator trajectories already share a coordinate frame.

## Results

| Sequence | Valid Ratio | Corr | Eval Poses | APE XY RMSE | RPE XY RMSE | RPE Rot RMSE | Pair Dir |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| city_summer_vs_city_night | 0.8626 | 0.8907 | 314 | 56.452329 | 58.875721 | 39.944988 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night` |
| city_night_vs_city_summer | 0.9451 | 0.6728 | 344 | 113.025033 | 83.274384 | 61.353515 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer` |
| city_night_vs_city_night | 0.9725 | 1.0000 | 354 | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night` |
| city_summer_vs_city_summer | 0.9725 | 1.0000 | 354 | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer` |
| village_summer_vs_village_winter | 0.9552 | 0.8483 | 1066 | 142.494418 | 90.732094 | 32.186772 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter` |
| village_winter_vs_village_summer | 0.9552 | 0.9448 | 1066 | 95.663280 | 75.319490 | 28.793026 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer` |
| village_winter_vs_village_winter | 0.9910 | 1.0000 | 1106 | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter` |
| village_summer_vs_village_summer | 0.9910 | 1.0000 | 1106 | 2.079706 | 1.315917 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer` |

## Artifact Index

- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/inputs/city_night_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/inputs/city_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_night/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/inputs/city_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/inputs/city_night_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_summer/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/inputs/city_night_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/inputs/city_night_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_night_vs_city_night/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/inputs/city_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/inputs/city_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_summer_vs_city_summer/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/inputs/village_winter_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/inputs/village_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_winter/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/inputs/village_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/inputs/village_winter_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_summer/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/inputs/village_winter_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/inputs/village_winter_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_winter_vs_village_winter/outputs/rpe_rot_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/outputs/matched_frames.csv`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/inputs/village_summer_gt_from_query.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/inputs/village_summer_est_from_matches.tum.txt`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/outputs/ape_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/outputs/rpe_trans_xy_raw.pdf`
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_summer_vs_village_summer/outputs/rpe_rot_raw.pdf`