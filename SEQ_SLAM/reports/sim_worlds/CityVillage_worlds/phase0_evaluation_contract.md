# Phase 0: Sim-Worlds Evaluation Contract

Date: 2026-03-28
Scope: City/Village simulator SeqSLAM benchmark
Status: Approved for execution baseline

## 1) Objective

Freeze one evaluation contract before further experiments so all comparisons are fair, reproducible, and directly comparable.

## 2) Canonical Data Contract

### 2.1 Dataset groups

- city_sim
- village_sim

### 2.2 Required run pairs (current baseline)

- city_sim_day_centerline vs city_sim_day_centerline
- city_sim_day_centerline vs city_sim_night_centerline
- village_sim_day_centerline_smooth vs village_sim_day_centerline_smooth
- village_sim_day_centerline_smooth vs village_sim_winter_centerline_smooth

### 2.3 Input format assumptions

- Oxford-like image folder layout per run.
- Timestamp-ordered image sequences.
- SeqSLAM-compatible input stream in mono_left.

## 3) Evaluation Procedure Contract

### 3.1 Script and command

- Script: SEQ_SLAM/pyseqslam/tune_sim_worlds.py
- Command: /Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py --auto-query-stride --no-cache

### 3.2 Parameter search space (frozen baseline)

- Sequence length: ds sweep including 10 and 50.
- Velocity bounds: vmin/vmax sweep with baseline winner at (0.8, 1.2).
- Rwindow: includes 10.
- Threshold: swept and selected by ranking score.

### 3.3 Ranking and quality fields

- tuning_pass
- rank_score
- valid_ratio
- corr
- norm_mae
- selected best params: ds, vmin, vmax, rwindow, threshold

## 4) Fairness Rules

- Same pipeline and command template used for all pairs.
- Auto query stride policy applied consistently.
- Pair-level outputs must include both tuning_summary.csv and best matching plot.
- No pair is considered complete without artifact presence and pass flag.

## 5) Required Artifacts

- Master summary table:
  - SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv
- Narrative report:
  - SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/report.md
- Per-pair outputs root:
  - SEQ_SLAM/pyseqslam/results/sim_worlds/

## 6) Acceptance Criteria

Phase 0 is considered complete when:

- All 4 required pairs are executed.
- All 4 pairs have tuning_pass = True.
- All 4 pairs have tuning_summary.csv and best plot artifacts.
- Summary and report files are updated.

## 7) Current Baseline Decision (from completed runs)

- Identity-condition sanity checks must always be run first.
- Cross-condition pairs are expected to degrade compared to identity pairs.
- Harder cross-condition pairs may require larger ds (observed ds=50 winners).

## 8) Next-Step Boundary

Any new sim-world experiment (new routes, new weather, or new model variants) must follow this Phase 0 contract unless explicitly versioned as a new protocol revision.
