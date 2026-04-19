# SeqSLAM Full Evaluation Progress

## 1) Goal (What this run is for)
This run is the unified SeqSLAM full evaluation pipeline for:
- Sim worlds (City and Village), with one-way map->query comparisons and sanity checks.
- Oxford dataset, with one-way map->query comparisons and sanity check.
- Evo-compatible exports and reports where possible.
- Clean final packaging in one bundle for cross-model comparison.

Run label:
- `seqslam_full_eval_2026-04-17_run1`

Top-level run folder:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1`

## 2) Locked Scope (Agreed matrix)
### Sim worlds (one-way only)
1. city_summer -> city_summer (sanity)
2. city_summer -> city_night
3. village_summer -> village_summer (sanity)
4. village_summer -> village_winter

### Oxford (one-way only)
1. 2014-05-14-13-46-12 -> 2014-05-14-13-46-12 (sanity)
2. 2014-05-14-13-46-12 -> 2014-06-23-15-36-04
3. 2014-05-14-13-46-12 -> 2014-06-26-08-53-56

Constraints agreed before run:
- No reverse-direction runs.
- Front camera policy for consistency across SLAM models.
- Oxford has no trajectory ground truth in current folders; proceed with available data.
- Use evo protocol settings as agreed; if GT is unavailable, mark evo as skipped for that track.
- Update shared cross-model CSVs for sim-world eval outputs.

## 3) Driver and Pipeline Design
Driver script:
- `SEQ_SLAM/reports/cross_model/scripts/run_seqslam_full_eval.py`

Intended execution stages:
1. Build run workspace under `cross_model/seqslam_full_eval_<run-label>/`.
2. Write sim-world pair input CSV.
3. Run sim-world tuning grid search.
4. Run sim-world evo evaluation and cross-model CSV updates.
5. Package sim-world outputs into final bundle section.
6. Run Oxford tuning for 3 agreed pairs.
7. Package Oxford outputs with explicit evo-skip note if GT is absent.
8. Final top-level summary/report for this run label.

## 4) Exact Sim-world Input for This Run
Source file:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/inputs/sim_world_pairs.csv`

Current content:
- city, city_summer, city_summer
- city, city_summer, city_night
- village, village_summer, village_summer
- village, village_summer, village_winter

## 5) Current Stage Status (Latest Known)
## Stage 1: Run folder bootstrap
Status: COMPLETE
Notes:
- Run folder created with `inputs/`, `logs/`, `.runtime/`.

## Stage 2: Sim-world tuning launch
Status: COMPLETE
Log:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/logs/sim_worlds_tune.log`

Observed outcome:
- All 4/4 sim-world pairs were processed to completion.
- Tuning report generated successfully.

Report artifacts:
- `SEQ_SLAM/reports/sim_worlds/SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning/report.md`
- `SEQ_SLAM/reports/sim_worlds/SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning/summary.csv`

Per-pair best tuning snapshot (from tuning report):
- city_summer vs city_summer: strong sanity match (corr ~1.0000, mae ~0.0000)
- city_summer vs city_night: moderate cross-condition match (corr ~0.3747)
- village_summer vs village_summer: strong sanity match (corr ~1.0000, mae ~0.0000)
- village_summer vs village_winter: strong cross-condition match (corr ~0.7726)

## Stage 3: Sim-world evo evaluation
Status: COMPLETE
Log:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/logs/sim_worlds_evo.log`

Primary report:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1_sim_worlds_evo.md`

Final outcome summary:
- Completed 4 SeqSLAM match evaluations.
- city_summer_vs_city_summer: valid_ratio=0.9725, APE=0.000000, RPE_trans=0.000000, RPE_rot=0.000000
- city_summer_vs_city_night: valid_ratio=0.8626, APE=117.554348, RPE_trans=111.762542, RPE_rot=85.050226
- village_summer_vs_village_summer: valid_ratio=0.9910, APE=0.000000, RPE_trans=0.000000, RPE_rot=0.000000
- village_summer_vs_village_winter: valid_ratio=0.9552, APE=173.794906, RPE_trans=152.112170, RPE_rot=51.437498

Operational fix applied during rerun:
- Installed `evo` in project `.venv`.
- Patched `eval_seqslam_sim_worlds.py` to resolve evo binaries from active interpreter env robustly.

## Stage 4: Sim-world packaging
Status: COMPLETE

Bundle output:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/sim_worlds`

## Stage 5: Oxford tuning
Status: COMPLETE

Oxford summary artifact:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/01_batch/summary.csv`

Final tuning outcomes:
- `2014-05-14-13-46-12_vs_2014-05-14-13-46-12`: rank=0.997517, valid_ratio=0.996586, corr=0.997922, norm_mae=0.000770
- `2014-05-14-13-46-12_vs_2014-06-23-15-36-04`: rank=0.811315, valid_ratio=0.985457, corr=0.598171, norm_mae=0.142729
- `2014-05-14-13-46-12_vs_2014-06-26-08-53-56`: rank=0.812349, valid_ratio=0.983553, corr=0.601292, norm_mae=0.138439

## Stage 6: Oxford packaging/report
Status: COMPLETE

Oxford bundle report:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/01_batch/report.md`

Per-pair packaged outputs:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-05-14-13-46-12/01_seqslam`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-23-15-36-04/01_seqslam`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-26-08-53-56/01_seqslam`

## Stage 7: Final consolidated completion report
Status: COMPLETE

Top-level run summary:
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/README.md`

## Stage 8: Oxford evo extension (post-run)
Status: COMPLETE (ALL 3 PAIRS)

What was added:
- New runner with batch support and GT wiring:
  - `SEQ_SLAM/reports/cross_model/scripts/run_oxford_evo_proxy.py`
- Batch result table:
  - `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/02_evo_batch/summary.csv`
  - `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/02_evo_batch/report.md`

Batch execution outcome (3 requested pairs):
- `2014-05-14-13-46-12_vs_2014-05-14-13-46-12`: proxy evo SUCCESS, exported_poses=2919
- `2014-05-14-13-46-12_vs_2014-06-23-15-36-04`: proxy evo SUCCESS, exported_poses=3388
- `2014-05-14-13-46-12_vs_2014-06-26-08-53-56`: proxy evo SUCCESS, exported_poses=2990

How full coverage was achieved:
- Added speed-invariant proxy alignment in runner (`--proxy-time-alignment normalized`).
- Run timelines are normalized to [0,1] and mapped onto proxy trajectory span.
- This supports same-route runs with different local speeds.

GT-mode wiring remains supported:
- Runner accepts per-run GT map CSV (`run_id,gt_tum`) and can execute `--mode gt` or `--mode auto`.
- GT remains the preferred final path when per-run Oxford GT trajectories are available.

## 6) Generated Artifacts So Far
### Run control artifacts
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/inputs/sim_world_pairs.csv`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/logs/sim_worlds_tune.log`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/logs/sim_worlds_evo.log`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1_sim_worlds_evo.md`

### Sim-world tuning artifacts
- `SEQ_SLAM/reports/sim_worlds/SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning/report.md`
- `SEQ_SLAM/reports/sim_worlds/SeqSLAM_full_eval_2026-04-17_run1/sim_worlds_tuning/summary.csv`
- Per-pair result directories under:
  - `SEQ_SLAM/pyseqslam/results/sim_worlds/city/`
  - `SEQ_SLAM/pyseqslam/results/sim_worlds/village/`

### Sim-world evo artifacts
- `SEQ_SLAM/reports/cross_model/pilot/seq_slam_2026-04-17_run1/`
- Per-pair `inputs/*.tum.txt`, `outputs/*.txt`, `outputs/*.pdf`, `outputs/*.zip`, and `outputs/matched_frames.csv`

### Sim-world packaged bundle section
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/sim_worlds/`

### Oxford tuning and packaged bundle section
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/01_batch/summary.csv`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/01_batch/report.md`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/`

### Oxford evo extension artifacts
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/02_evo_batch/summary.csv`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/02_evo_batch/report.md`
- `SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-05-14-13-46-12/02_evo_proxy/`

## 7) Operational Timeline (High-level)
1. Sim-world tuning started and iterated full grid across city and village pairs.
2. Sim-world tuning finished successfully (4/4).
3. Evo stage initially failed due to missing `evo_ape`; environment and executable resolution were fixed.
4. Evo stage rerun completed successfully for all 4 sim-world pairs.
5. Sim-world bundle packaging completed.
6. Oxford stage resumed and completed all 3 agreed pairs.
7. Oxford packaged report and per-pair artifacts were created.
8. Top-level bundle README was written, and the full run completed successfully.

## 8) Recovery / Resume Plan
## Current continuation mode
Run continuation used in-place resume on existing run label and is now complete.

Resume command in use:
1. `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python SEQ_SLAM/reports/cross_model/scripts/run_seqslam_full_eval.py --run-label 2026-04-17_run1 --resume-existing --skip-sim-worlds`

Expected remaining behavior:
- None. All planned stages are complete for run label `2026-04-17_run1`.

## 9) Completion Definition (Done Criteria)
This run is considered complete when all are true:
1. Sim-world: tuning + evo metrics + evo plots/tables + packaged section completed.
2. Oxford: tuning completed for 3 pairs and packaged section completed.
3. Oxford section includes evo outputs for all 3 agreed pairs, with mode and alignment notes.
4. Shared cross-model CSV updates from sim-world evo are present.
5. Top-level final report exists in this run folder and references all produced artifacts.

## 10) Notes for Cross-model Comparison Readiness
For fair cross-model comparison, this run already aligns with:
- Front-camera consistency policy.
- One-way map->query protocol.
- Explicit sanity checks for both sim families and Oxford.

Remaining to become fully comparison-ready:
- No open pipeline stages remain for this run bundle.
