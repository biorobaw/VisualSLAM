# ORB-SLAM vs SEQ-SLAM evo Settings

Date: 2026-04-17

## Purpose

This note summarizes the `evo` settings currently used in the ORB-SLAM and SEQ-SLAM folders so the cross-model evaluation protocol can be standardized.

## Current Settings

| Lane | Script | Metrics | Sync | Alignment | Scale correction | Projection | Metric mode | Plot mode | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ORB-SLAM | `ORB_SLAM/run_oxford.py` | APE, RPE | none explicit | `--align` | `--correct_scale` | none explicit | evo default | none explicit | Aligns both APE and RPE. Saves zip only. |
| ORB-SLAM | `ORB_SLAM/run_webots.py` | APE only | none explicit | `--align` | `--correct_scale` | none explicit | evo default | none explicit | No RPE in this script. |
| ORB-SLAM | `ORB_SLAM/compute_metrics.py` | APE, RPE | `--sync` | APE only | APE only | none explicit | evo default | none | APE uses align + scale correction, RPE does not. |
| ORB-SLAM | `ORB_SLAM/comparative_analysis.py` | trajectory plot only | none | none | none | XY plot | n/a | `xy` | Uses `evo_traj`, not a metric run. |
| SEQ-SLAM | `SEQ_SLAM/pyseqslam/eval_seqslam_sim_worlds.py` | APE, RPE trans, RPE rot | none explicit | none | none | `--project_to_plane xy` for APE and RPE trans | `trans_part`, `angle_deg` | `xy` | This is the current raw sim-world metric lane. |
| SEQ-SLAM | `SEQ_SLAM/reports/cross_model/scripts/run_sim_worlds_evo_rerun.py` | APE, RPE trans, RPE rot | none explicit | `-a` | none explicit | none | `full`, `trans_part`, `angle_deg` | `xyz` | This is an aligned rerun/check lane, not the same as the raw sim-world report lane. |

## Main Mismatches

1. ORB-SLAM is not internally consistent.
   `run_oxford.py` aligns both APE and RPE, `run_webots.py` computes only APE, and `compute_metrics.py` aligns APE but leaves RPE unaligned.

2. ORB-SLAM and SEQ-SLAM are not using the same evaluation frame.
   The current SEQ-SLAM sim-world report lane uses raw XY metrics without alignment, while ORB-SLAM scripts generally use alignment and scale correction.

3. ORB-SLAM leaves several evo defaults implicit.
   There is no explicit `-r trans_part` or `-r angle_deg` split in the runner scripts, and no explicit `--project_to_plane xy` for simulator comparisons.

4. There are effectively two SEQ-SLAM evo protocols in the repo.
   The public sim-world evaluation script is raw XY without alignment, while the rerun script is aligned in full 3D.

## Recommended Standard For Fair Cross-Model Sim-World Comparison

For the simulator worlds, use one canonical policy for every model:

- Format: `tum`
- Sync: explicit `--sync` if timestamps can differ across exported trajectories
- Alignment: none
- Scale correction: none
- Translation metrics: `--project_to_plane xy`
- APE mode: `-r trans_part`
- RPE translation mode: `-r trans_part`
- RPE rotation mode: `-r angle_deg`
- Plot mode: `xy`

Reason:
The simulator trajectories already share a common coordinate frame, so raw XY error is the cleanest cross-model comparison. Allowing alignment or scale correction for only one model would make the numbers easier to optimize but less fair to compare.

## If You Need A Separate "Tracking Quality" Protocol

If a model cannot be fairly judged in the shared raw frame, create a second protocol and label it clearly:

- `aligned_sim3_eval`
- use alignment for all models
- use scale correction for all monocular models, or for none
- do not mix those numbers with the raw-frame benchmark table

## Script References

- `ORB_SLAM/run_oxford.py`
- `ORB_SLAM/run_webots.py`
- `ORB_SLAM/compute_metrics.py`
- `ORB_SLAM/comparative_analysis.py`
- `SEQ_SLAM/pyseqslam/eval_seqslam_sim_worlds.py`
- `SEQ_SLAM/reports/cross_model/scripts/run_sim_worlds_evo_rerun.py`
