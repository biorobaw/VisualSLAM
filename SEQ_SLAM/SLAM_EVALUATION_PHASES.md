# VisualSLAM Evaluation Completion Plan

This document defines the phased execution plan to finish a fair, reproducible comparison of SLAM models using a shared trajectory format and common metrics.

## 1. Project Goal

Build and run one unified evaluation pipeline for all target SLAM systems that:

- converts outputs to one canonical trajectory format (TUM style),
- applies consistent synchronization and alignment rules,
- computes ATE and RPE in a repeatable way,
- produces comparison tables and plots suitable for team reporting.

## 2. Definition of Success

The project is successful when all items below are true:

- Every model can export trajectories in the same canonical format.
- Every evaluated sequence has ground-truth and estimated trajectories validated by checks.
- ATE and RPE are computed with one shared script and one shared config.
- Results can be reproduced from a clean checkout by following one runbook.
- Final report includes per-sequence metrics, aggregate metrics, and visual overlays.

## 3. Scope and Non-Scope

### In scope

- TUM-style trajectory standardization.
- Conversion scripts for each model output format.
- Evo-based ATE/RPE evaluation.
- Alignment and synchronization policy.
- Reporting and reproducibility documentation.

### Out of scope (for this phase)

- Novel metric research beyond ATE/RPE.
- Rewriting SLAM algorithms.
- Real-time system optimization.

## 4. Work Phases

## Phase 0 - Freeze Evaluation Contract (1-2 days)

### Objective

Lock all assumptions before implementation to avoid invalid comparisons later.

### Tasks

- Define canonical trajectory schema: timestamp tx ty tz qx qy qz qw.
- Define timestamp unit and precision policy (seconds, monotonic, no duplicates).
- Define coordinate conventions: axis directions, unit scale, frame naming.
- Define mandatory metrics: ATE RMSE, RPE translation, RPE rotation.
- Define comparison modes:
  - raw (no alignment),
  - SE(3)-aligned,
  - Sim(3)-aligned only if scale drift applies.
- Define sync tolerance and sampling policy.

### Deliverables

- Evaluation spec markdown file.
- Team sign-off in meeting notes.

### Exit criteria

- All teammates agree to one evaluation contract.

---

## Phase 1 - Data and Ground-Truth Audit (1-2 days)

### Objective

Ensure all required data exists and is valid before model conversion/evaluation.

### Tasks

- Build inventory of datasets/sequences to evaluate.
- Confirm availability of ground-truth trajectory for each sequence.
- Check GT file quality:
  - monotonic timestamps,
  - finite values only,
  - normalized quaternions,
  - realistic path length.
- Define train/validation/test or benchmark split (if applicable).

### Deliverables

- Dataset inventory table.
- Ground-truth quality audit report.

### Exit criteria

- Every target sequence has validated GT and ready input data.

---

## Phase 2 - Canonical Conversion Layer (2-4 days)

### Objective

Create reliable conversion adapters from each SLAM model output to canonical TUM-style files.

### Tasks

- For each model (ORB_SLAM, RAT_SLAM, SEQ_SLAM, others), map native output fields to canonical fields.
- Implement one converter script per model (or one multi-backend converter with model-specific parsers).
- Add strict validator checks in conversion output:
  - increasing timestamps,
  - no NaN/Inf,
  - quaternion norm close to 1,
  - minimum sample count.
- Add clear error messages and non-zero exits for invalid files.

### Deliverables

- Converter scripts and validation utility.
- Sample converted trajectory files for one sequence per model.

### Exit criteria

- All target models can produce valid canonical trajectory files.

---

## Phase 3 - Evo Pilot Pipeline (1-2 days)

### Objective

Prove end-to-end evaluation works on a small pilot before scaling.

### Tasks

- Install and pin evo version in environment docs.
- Build one script/command template that:
  - loads GT + estimate,
  - applies sync,
  - applies configured alignment mode,
  - computes ATE and RPE,
  - writes metrics + plots to output folder.
- Run pilot on one model and one sequence.
- Verify repeatability by rerunning and comparing outputs.

### Deliverables

- Pilot results folder with metrics and plots.
- Short pilot note: what worked, what changed.

### Exit criteria

- Pilot run is reproducible and passes sanity checks.

---

## Phase 4 - Fairness and Robustness Protocol (1-2 days)

### Objective

Prevent misleading leaderboard results caused by inconsistent alignment/sync choices.

### Tasks

- Add controlled ablation runs:
  - no alignment vs SE(3) alignment,
  - default sync tolerance vs stricter tolerance.
- Define fixed evaluation windows per sequence.
- Define missing-data policy (drop, interpolate, or fail) and keep it fixed.
- Add pass/fail quality gates for each run.

### Deliverables

- Fairness protocol markdown file.
- Accepted default evaluation settings.

### Exit criteria

- Team-approved fairness rules used for all models.

---

## Phase 5 - Full Batch Evaluation (3-7 days)

### Objective

Run the complete benchmark matrix across models and sequences.

### Tasks

- Execute evaluation matrix (model x sequence x setting).
- Auto-save outputs in predictable folder structure.
- Generate machine-readable summary CSV/JSON.
- Capture runtime, dropped frames, and pass/fail flags.

### Deliverables

- Full results table.
- Aggregate plots (trajectory overlays, ATE/RPE distributions).

### Exit criteria

- Complete matrix executed or explicitly documented exclusions.

---

## Phase 6 - ROS Compatibility Adapter (parallel track, 2-5 days)

### Objective

Integrate models without stable ROS support through a Python wrapper export path.

### Tasks

- For non-ROS model, implement Python wrapper that exports canonical trajectory directly.
- If ROS exists, support optional ROS bag to trajectory conversion.
- Keep ROS and non-ROS paths feeding the same evaluator interface.

### Deliverables

- Wrapper script and usage docs.
- One verified run from non-ROS model into evaluator.

### Exit criteria

- ROS availability is not a blocker for benchmark inclusion.

---

## Phase 7 - Reproducibility and CI Checks (1-3 days)

### Objective

Make reruns dependable for teammates and future report updates.

### Tasks

- Create one runbook with exact commands.
- Pin core dependencies and versions.
- Add smoke test for converter + evaluator on tiny sample trajectories.
- Add checksum or manifest for key output artifacts.

### Deliverables

- Reproducibility runbook.
- Basic automated smoke checks.

### Exit criteria

- Another teammate can reproduce pilot and one batch subset unassisted.

---

## Phase 8 - Final Report and Handoff (1-2 days)

### Objective

Package findings into a clear technical summary for group/professor use.

### Tasks

- Produce final tables with per-sequence and aggregate metrics.
- Include interpretation notes: where each model wins/loses and why.
- Document limitations and known threats to validity.
- Publish next-step recommendations.

### Deliverables

- Final evaluation report markdown/PDF.
- Presentation-ready figures.

### Exit criteria

- Team can present methods, fairness, and results confidently.

## 5. Suggested Timeline (2-3 weeks)

- Week 1: Phase 0, Phase 1, start Phase 2.
- Week 2: finish Phase 2, Phase 3, Phase 4.
- Week 3: Phase 5, Phase 6, Phase 7, Phase 8.

## 6. Team Task Split (example)

- Person A: TUM spec and converter validation.
- Person B: evo pipeline and fairness protocol.
- Person C: ROS/non-ROS wrapper and integration.
- Person D: reporting, aggregation, and documentation.

## 7. Risk Register

- Risk: inconsistent coordinate frames across models.
  - Mitigation: contract in Phase 0 plus validation checks.
- Risk: missing or noisy GT for some sequences.
  - Mitigation: Phase 1 audit and exclusion policy.
- Risk: model cannot export ROS-compatible data.
  - Mitigation: Python wrapper path in Phase 6.
- Risk: non-reproducible results due to environment drift.
  - Mitigation: pinned dependencies and smoke tests.

## 8. Immediate Next Actions (start now)

1. Create Evaluation Spec file and freeze conventions.
2. Implement first converter for one model and validate output.
3. Run first evo pilot and store metrics/plots.
4. Review pilot in team meeting and lock fairness defaults.

## 9. Completion Checklist

- [ ] Evaluation spec approved.
- [ ] All model converters implemented.
- [ ] Conversion validators pass.
- [ ] Pilot run reproducible.
- [ ] Fairness protocol approved.
- [ ] Full benchmark matrix executed.
- [ ] Final tables and plots generated.
- [ ] Final report delivered.
