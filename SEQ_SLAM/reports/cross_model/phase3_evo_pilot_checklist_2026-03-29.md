# Phase 3 Evo Pilot Checklist

Date: 2026-03-29

## Pilot target selection

- Sequence ID: city_sim_day_centerline
- Ground truth file: SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_sim_day_centerline/inputs/seqslam_city_day.tum.txt
- Model for first pilot: SEQ_SLAM
- Owner: SEQ_SLAM lane (this workspace)

## Preconditions

- [ ] Canonical trajectory contract signed off (team)
- [x] Model handoff template completed
- [x] Canonical estimate trajectory exported
- [x] GT trajectory validated
- [x] evo installed in environment

## Execution steps

- [x] Run ATE (raw)
- [x] Run ATE (SE3 aligned)
- [x] Run RPE translation
- [x] Run RPE rotation
- [x] Save outputs under `reports/cross_model/pilot/<model>/<sequence>/outputs/`
- [x] Add one row to cross_model_results_template.csv

## Quality checks

- [x] Metrics generated with no runtime errors
- [ ] Plots generated
- [ ] Repeat run gives matching metrics within tolerance
- [x] Notes captured for any alignment/sync caveats

## Done criteria

Pilot is complete when all execution steps and quality checks are checked.
