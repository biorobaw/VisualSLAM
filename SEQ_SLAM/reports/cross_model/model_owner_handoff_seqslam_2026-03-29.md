# Model Owner Handoff - SEQ_SLAM

## Model

- Model name: SEQ_SLAM (sim-world trajectory source)
- Owner: SEQ_SLAM lane (this workspace)
- Date: 2026-03-29

## Native output description

- Output file path(s):
  - SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/poses.csv
  - SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/poses.csv
  - SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/poses.csv
  - SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/poses.csv
- Native columns/order: frame_id, x, y, yaw_rad
- Units for translation: simulator world units (assumed meters for current protocol)
- Rotation representation: yaw in radians (2D heading)
- Timestamp source and units: frame_id-based synthetic time (frame_id/fps or frame_id direct)

## Mapping to canonical TUM format

- timestamp <- frame_id (or (frame_id-1)/fps)
- tx ty tz <- x, y, 0.0
- qx qy qz qw <- yaw-only quaternion (0, 0, sin(yaw/2), cos(yaw/2))

## Known assumptions / caveats

- Origin behavior: local simulator frame per run
- Coordinate frame notes: 2D route projected to 3D with z=0
- Missing fields or inferred fields: z, roll, and pitch are not present and are inferred as zero

## Validation results

- [x] Monotonic timestamps (frame_id monotonic)
- [x] No NaN/Inf (x, y, yaw_rad finite in sampled run sets)
- [x] Quaternion normalized (by construction from yaw)
- [x] Minimum sample count met (city: 364, village: 1116)

## Produced artifacts

- Canonical estimate file:
  - Generated via script: SEQ_SLAM/reports/cross_model/scripts/convert_sim_poses_to_tum.py
- Validation log:
  - counts and monotonic/finite checks recorded in chat run for 4 sim runs
- Sample plot/preview:
  - pending evo pilot output

## Ready for evo pilot

- [x] Yes
- [ ] No (blocker listed below)

Blockers:

- Need agreed fps/timestamp policy finalized in contract sign-off.
