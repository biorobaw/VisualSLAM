# Cross-Model Trajectory Contract (v1)

Date: 2026-03-29
Status: Draft for team sign-off

## Goal

Define one canonical trajectory format and evaluation assumptions so ORB_SLAM, RAT_SLAM, and SEQ_SLAM outputs can be compared fairly.

## Canonical file format

Use TUM trajectory text format, one pose per line:

`timestamp tx ty tz qx qy qz qw`

Rules:

- Values are space-separated.
- `timestamp` is in seconds (float), strictly increasing.
- Translation (`tx ty tz`) is in meters.
- Quaternion (`qx qy qz qw`) must be normalized.
- No header line in final exported files.

## Coordinate and frame conventions

- Estimated and GT trajectories must represent the same physical frame semantics.
- Keep frame naming documented per model export.
- If a model uses a different origin, alignment is handled during evaluation, not by ad hoc manual edits.
- No axis swapping or sign flipping is allowed unless documented and reviewed.

## Required validation checks before evaluation

- Timestamps monotonic increasing.
- No NaN or Inf values.
- Quaternion norm close to 1.0.
- Minimum 100 poses for a valid run unless explicitly marked as short sequence test.

## Evaluation modes to report

For each model/sequence pair, report both:

1. Raw (no alignment)
2. SE(3) aligned

Optional:

- Sim(3) aligned only for monocular/scale-ambiguous cases, clearly marked in report.

## Metrics to report

- ATE RMSE
- RPE translation (RMSE)
- RPE rotation (RMSE)

## Output artifact requirements

Per evaluated run:

- Canonical estimate file (`*.tum.txt`)
- Canonical GT file (`*.tum.txt`)
- Evo metrics output file
- Evo plot(s)
- One row in cross-model summary table

## Ownership mapping

- ORB_SLAM owner: TBD
- RAT_SLAM owner: TBD
- SEQ_SLAM owner: TBD

## Sign-off checklist

- [ ] Team accepted schema and units
- [ ] Team accepted frame/alignment rules
- [ ] Team accepted mandatory metrics
- [ ] Team accepted validation gates
