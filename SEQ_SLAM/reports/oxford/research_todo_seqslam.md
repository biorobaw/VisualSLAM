# Oxford SeqSLAM Research To-Do (11 Available Runs)

This checklist is for documenting the full Oxford SeqSLAM study in three phases.
Use this file as the master tracker for decisions, runs, and results.

## 0) Dataset Inventory (Current, Tagged Folder Names)

Mark each run as verified before running experiments.

- [x] 2014-05-06-12-54-54__clouds_sun
- [x] 2014-05-06-13-09-52__clouds_sun
- [x] 2014-05-06-13-14-58__clouds_poor_gps_sun
- [x] 2014-05-14-13-46-12__sun
- [x] 2014-05-14-13-50-20__sun
- [x] 2014-05-19-12-51-39__poor_gps_sun
- [x] 2014-06-23-15-14-44__sun
- [x] 2014-06-23-15-36-04__sun
- [x] 2014-06-23-15-41-25__sun
- [x] 2014-06-26-08-53-56__overcast
- [x] 2014-06-26-09-24-58__overcast

Verification checks per run:
- [x] `mono_left` exists
- [x] image count recorded
- [x] obvious extraction/path issues resolved

---

## 1) Experiment-Wide Setup (Do Once)

### 1.1 Decide global defaults
- [x] Finalize baseline reference candidate (`2014-05-14-13-46-12__sun` recommended)
- [x] Confirm initial parameter grid (`ds`, `vmin/vmax`, `Rwindow`, threshold)
- [x] Define length-balancing policy (`--auto-query-stride` by default)
- [x] Define quality ranking metric (valid ratio + diagonal correlation + normalized MAE)

### 1.2 Reproducibility settings
- [ ] Keep one command template for all runs
- [ ] Use stable output directory naming convention
- [ ] Save tuning CSV + best plot for every comparison
- [ ] Track script version / git commit hash for each experiment batch

### 1.3 Reporting fields (must log every run)
- [ ] Reference run
- [ ] Query run
- [ ] Query stride used
- [ ] Best params: `ds`, `vmin`, `vmax`, `Rwindow`, threshold
- [ ] Metrics: valid count, valid ratio, corr, MAE, normalized MAE
- [ ] Notes on failure modes (drift, off-diagonal streaks, sparse matches)

---

## 2) Phase 1 — Fixed-Reference (10 Comparisons)

Goal: quickly establish stable parameters and a baseline performance profile.

### 2.1 Choose the reference run
- [x] Confirm final reference run (recommended: `2014-05-14-13-46-12__sun`)
- [x] Justify why chosen (clean condition, good route coverage, not too short)

### 2.2 Run fixed-reference comparisons
For 11 total runs, fixed-reference gives 10 comparisons (excluding self-match).

- [x] ref vs `2014-05-06-12-54-54__clouds_sun`
- [x] ref vs `2014-05-06-13-09-52__clouds_sun`
- [x] ref vs `2014-05-06-13-14-58__clouds_poor_gps_sun`
- [x] ref vs `2014-05-14-13-50-20__sun`
- [ ] ref vs `2014-05-19-12-51-39__poor_gps_sun`
- [ ] ref vs `2014-06-23-15-14-44__sun`
- [ ] ref vs `2014-06-23-15-36-04__sun`
- [ ] ref vs `2014-06-23-15-41-25__sun`
- [ ] ref vs `2014-06-26-08-53-56__overcast`
- [ ] ref vs `2014-06-26-09-24-58__overcast`

### 2.3 Phase 1 quality gate
- [ ] All 10 runs finished without path/runtime errors
- [ ] Each run has `tuning_summary.csv`
- [ ] Each run has best-match plot
- [ ] Build one Phase 1 summary table (all 10 rows)
- [ ] Identify provisional global parameter set from top performers

Deliverables:
- [ ] `Phase1_summary.csv` (combined)
- [ ] short write-up: what worked, what failed, what to carry forward

---

## 3) Phase 2 — Targeted Hard Pairs

Goal: stress-test SeqSLAM on difficult condition gaps.

### 3.1 Hard pair categories
- [ ] poor-gps vs sun
- [ ] overcast vs sun
- [ ] clouds vs sun

### 3.2 Recommended targeted pairs (from available runs)
poor-gps vs sun:
- [ ] `2014-05-19-12-51-39__poor_gps_sun` vs `2014-05-14-13-46-12__sun`
- [ ] `2014-05-06-13-14-58__clouds_poor_gps_sun` vs `2014-06-23-15-14-44__sun`

overcast vs sun:
- [ ] `2014-06-26-08-53-56__overcast` vs `2014-05-14-13-46-12__sun`
- [ ] `2014-06-26-09-24-58__overcast` vs `2014-06-23-15-36-04__sun`

clouds vs sun:
- [ ] `2014-05-06-12-54-54__clouds_sun` vs `2014-05-14-13-46-12__sun`
- [ ] `2014-05-06-13-09-52__clouds_sun` vs `2014-06-23-15-41-25__sun`

### 3.3 Per-pair tuning policy
- [ ] Start from Phase 1 global params
- [ ] Retune threshold first
- [ ] If still weak, retune `ds`
- [ ] If still weak, expand velocity range
- [ ] Record exact change path (what was changed and why)

Deliverables:
- [ ] `Phase2_hardpairs_summary.csv`
- [ ] one comparison chart (Phase 1 baseline vs Phase 2 hard-case results)

---

## 4) Phase 3 — Full Pairwise (Optional, High Coverage)

Goal: complete statistical coverage across all available runs.

With 11 runs, unordered full pairwise count is:

$$\binom{11}{2} = 55$$

### 4.1 Decision gate before starting
- [ ] Phase 1 + 2 results are stable enough to justify full sweep
- [ ] Compute budget/time budget approved
- [ ] Storage budget approved (plots + CSVs)

### 4.2 Execution checklist
- [ ] Generate all 55 pair combinations
- [ ] Run with same evaluation protocol as Phase 1/2
- [ ] Auto-skip already completed pairs
- [ ] Re-run failed pairs only
- [ ] Validate all pair outputs exist

### 4.3 Final statistical outputs
- [ ] Overall distribution of valid ratio
- [ ] Overall distribution of correlation and normalized MAE
- [ ] Condition-group breakdown (sun-sun, sun-overcast, sun-poor-gps, clouds-sun, etc.)
- [ ] Top 5 and bottom 5 pair analyses with visual examples

Deliverables:
- [ ] `Phase3_full55_summary.csv`
- [ ] final aggregate plots and short interpretation section

---

## 5) Run Log Template (Copy Per Comparison)

Use one block per experiment:

- Date/time:
- Reference run:
- Query run:
- Query stride:
- Command used:
- Best params (`ds`, `vmin`, `vmax`, `Rwindow`, threshold):
- Valid count / ratio:
- Corr:
- MAE / normalized MAE:
- Runtime:
- Output folder:
- Notes (failure mode, route overlap issues, observations):

---

## 6) Weekly Documentation Checklist

- [ ] Update this tracker after every run session
- [ ] Push result artifacts and summary CSV updates
- [ ] Write 3–5 bullet weekly findings
- [ ] Capture parameter changes made that week
- [ ] List blockers and next experiments

This keeps your final paper/report preparation fast and transparent.

---

## 7) Run Log Entries

### Run 001

- Date/time: 2026-02-25
- Reference run: `2014-05-14-13-46-12__sun`
- Query run: `2014-05-06-12-54-54__clouds_sun`
- Query stride: 2 (auto)
- Command used: `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py --reference-run 2014-05-14-13-46-12__sun --query-run 2014-05-06-12-54-54__clouds_sun --auto-query-stride`
- Best params (`ds`, `vmin`, `vmax`, `Rwindow`, threshold): `10`, `0.80`, `1.20`, `10`, `1.00`
- Valid count / ratio: `1219 / 1937` (`62.93%`)
- Corr: `0.2534`
- MAE / normalized MAE: `872.97` / `0.4133`
- Runtime: DD build/load + preprocessing `43.28s` (matcher sweep completed)
- Output folder: `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-12-54-54__clouds_sun/`
- Notes (failure mode, route overlap issues, observations): first run required no-cache fallback due legacy `.mat` cache layout; one runtime warning in matcher (`invalid value encountered in scalar divide`) but run completed and produced ranked results.

### Experiment: Sun Reference vs Clouds/Sun Query (2014-05-06-13-09-52)

- Date/time: 2026-02-25
- Reference run: `2014-05-14-13-46-12__sun`
- Query run: `2014-05-06-13-09-52__clouds_sun`
- Query stride: 2 (auto)
- Command used: `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py --reference-run 2014-05-14-13-46-12__sun --query-run 2014-05-06-13-09-52__clouds_sun --auto-query-stride`
- Best params (`ds`, `vmin`, `vmax`, `Rwindow`, threshold): `20`, `0.80`, `1.20`, `10`, `1.00`
- Valid count / ratio: `1197 / 1907` (`62.77%`)
- Corr: `0.2455`
- MAE / normalized MAE: `904.58` / `0.4283`
- Runtime: DD build/load + preprocessing `43.19s` (matcher sweep completed)
- Output folder: `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-09-52__clouds_sun/`
- Notes (failure mode, route overlap issues, observations): legacy cache fallback was triggered again; one runtime warning in matcher (`invalid value encountered in scalar divide`) appeared but full ranked outputs were generated.

### Experiment: Sun Reference vs Clouds/Poor-GPS Query (2014-05-06-13-14-58)

- Date/time: 2026-02-25
- Reference run: `2014-05-14-13-46-12__sun`
- Query run: `2014-05-06-13-14-58__clouds_poor_gps_sun`
- Query stride: 1 (auto)
- Command used: `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py --reference-run 2014-05-14-13-46-12__sun --query-run 2014-05-06-13-14-58__clouds_poor_gps_sun --auto-query-stride`
- Best params (`ds`, `vmin`, `vmax`, `Rwindow`, threshold): `20`, `0.30`, `2.00`, `10`, `1.00`
- Valid count / ratio: `1262 / 2048` (`61.62%`)
- Corr: `0.2368`
- MAE / normalized MAE: `861.89` / `0.4081`
- Runtime: DD build/load + preprocessing `46.65s` (matcher sweep completed)
- Output folder: `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-14-58__clouds_poor_gps_sun/`
- Notes (failure mode, route overlap issues, observations): legacy cache fallback appeared again; one matcher runtime warning (`invalid value encountered in scalar divide`) was printed, but all ranked outputs and artifacts were generated successfully.

### Experiment: Sun Reference vs Sun Query (2014-05-14-13-50-20)

- Date/time: 2026-02-25
- Reference run: `2014-05-14-13-46-12__sun`
- Query run: `2014-05-14-13-50-20__sun`
- Query stride: 1 (auto)
- Command used: `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py --reference-run 2014-05-14-13-46-12__sun --query-run 2014-05-14-13-50-20__sun --auto-query-stride`
- Best params (`ds`, `vmin`, `vmax`, `Rwindow`, threshold): `10`, `0.80`, `1.20`, `10`, `1.00`
- Valid count / ratio: `245 / 284` (`86.27%`)
- Corr: `0.0284`
- MAE / normalized MAE: `717.82` / `0.3399`
- Runtime: DD build/load + preprocessing `23.27s` (matcher sweep completed)
- Output folder: `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-14-13-50-20__sun/`
- Notes (failure mode, route overlap issues, observations): legacy cache fallback appeared again; one matcher runtime warning (`invalid value encountered in scalar divide`) was printed, but all ranked outputs and artifacts were generated successfully.
