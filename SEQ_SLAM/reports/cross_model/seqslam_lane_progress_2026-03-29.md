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
- Added SeqSLAM model owner handoff:
  - SEQ_SLAM/reports/cross_model/model_owner_handoff_seqslam_2026-03-29.md
- Added populated phase-1 audit rows for available sim GT sources:
  - SEQ_SLAM/reports/cross_model/phase1_data_gt_audit_current_2026-03-29.csv

## Ready now

- SeqSLAM lane is ready for first evo pilot execution once team confirms GT/estimate pairing policy for pilot scoring.

## Waiting on team

- Team sign-off on trajectory contract v1.
- ORB_SLAM and RAT_SLAM owner handoffs.
- Shared pilot sequence choice and final GT assignment across models.
