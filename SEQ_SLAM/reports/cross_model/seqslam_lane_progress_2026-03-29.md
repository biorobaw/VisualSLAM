# SEQ_SLAM Lane Progress Update

Date: 2026-03-29

## Completed in this lane

- Located native trajectory sources for sim-worlds:
  - city_sim_day_centerline poses.csv
  - city_sim_night_centerline poses.csv
  - village_sim_day_centerline_smooth poses.csv
  - village_sim_winter_centerline_smooth poses.csv
- Verified data quality in native files:
  - frame_id monotonic: yes
  - finite values in x/y/yaw_rad: yes
  - pose counts: city=364, village=1116
- Added SeqSLAM converter script:
  - SEQ_SLAM/reports/cross_model/scripts/convert_sim_poses_to_tum.py
- Generated sample canonical trajectory for pilot:
  - SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_sim_day_centerline/inputs/seqslam_city_day.tum.txt
- Completed evo pilot sanity execution (self-check with distinct GT/EST filenames):
  - outputs folder: SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_sim_day_centerline/outputs
  - APE raw rmse: 0.0
  - APE SE3 rmse: 0.0
  - RPE trans rmse: 0.0
  - RPE rot rmse: 0.0
- Completed evo non-trivial execution (cross-route check):
  - GT: city_sim_day_centerline, EST: village_sim_day_centerline_smooth
  - APE raw rmse: 630.044376
  - APE SE3 rmse: 80.586008
  - RPE trans rmse: 0.587499
  - RPE rot rmse: 4.567549
- Added SeqSLAM model owner handoff:
  - SEQ_SLAM/reports/cross_model/model_owner_handoff_seqslam_2026-03-29.md
- Added populated phase-1 audit rows for available sim GT sources:
  - SEQ_SLAM/reports/cross_model/phase1_data_gt_audit_current_2026-03-29.csv

## Ready now

- SeqSLAM lane completed first evo sanity pilot and is ready for cross-model pilot run with non-identical GT/estimate trajectories.

## Waiting on team

- Team sign-off on trajectory contract v1.
- ORB_SLAM and RAT_SLAM owner handoffs.
- Shared pilot sequence choice and final GT assignment across models.
