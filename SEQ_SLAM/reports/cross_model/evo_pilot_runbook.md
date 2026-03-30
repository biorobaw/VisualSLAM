# Evo Pilot Runbook (Cross-Model)

Date: 2026-03-29

## Objective

Run one reproducible cross-model pilot using canonical TUM trajectories and produce ATE/RPE outputs.

## Inputs required

- Ground-truth trajectory in canonical TUM format
- Estimated trajectory in canonical TUM format
- Chosen sequence ID
- Chosen model ID

## Environment

1. Activate project environment:

```bash
source /Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/activate
```

2. Install evo if missing:

```bash
pip install evo
```

## Suggested folder layout

- `SEQ_SLAM/reports/cross_model/pilot/<model>/<sequence>/inputs/`
- `SEQ_SLAM/reports/cross_model/pilot/<model>/<sequence>/outputs/`

## Pilot commands (example)

ATE (SE(3) aligned):

```bash
evo_ape tum gt.tum.txt est.tum.txt -a -r full --save_results ape_results.zip --plot --plot_mode xyz
```

RPE translation (SE(3) aligned):

```bash
evo_rpe tum gt.tum.txt est.tum.txt -a -r trans_part --save_results rpe_trans_results.zip --plot --plot_mode xyz
```

RPE rotation (SE(3) aligned):

```bash
evo_rpe tum gt.tum.txt est.tum.txt -a -r angle_deg --save_results rpe_rot_results.zip --plot --plot_mode xyz
```

## Required pilot outputs

- ATE result archive
- RPE translation result archive
- RPE rotation result archive
- Plots exported to output folder
- One populated row in cross-model summary CSV

## Repeatability check

Run same commands twice and confirm metric equality within tiny tolerance.

## Acceptance criteria

- Pilot command set runs without errors
- Metrics generated for at least one model/sequence pair
- Summary row updated
- Owner handoff template completed for pilot model
