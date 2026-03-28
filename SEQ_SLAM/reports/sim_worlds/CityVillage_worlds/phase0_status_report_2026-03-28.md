# Sim-Worlds Phase 0 Status Report

Date: 2026-03-28
Protocol: city_village_worlds_auto_stride
Reference contract: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/phase0_evaluation_contract.md

## 1) What Was Done

- Built and used two controlled Webots worlds:
  - City: day and night
  - Village: day/summer and winter
- Collected matched route traversals and packaged runs in SeqSLAM-compatible Oxford-like layout.
- Executed full tuning/evaluation for 4 required baseline pairs.
- Generated and stored per-pair tuning summaries and best-match plots.
- Consolidated all results into one summary table and narrative report.

## 2) What Was Accomplished

- Baseline matrix completed: 4/4 pairs.
- Quality gate status: 4/4 tuning_pass = True.
- Artifacts complete for every pair:
  - tuning_summary.csv present
  - sim_worlds_tuning_best_matchings.png present
- Sanity-check behavior validated:
  - Same-condition pairs are near-perfect.
  - Cross-condition pairs degrade in expected, interpretable ways.

## 3) Results Summary (from summary.csv)

Source: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv

### Aggregate

- Pairs evaluated: 4
- Passed pairs: 4
- Average valid_ratio: 0.9454
- Average corr: 0.9232
- Average norm_mae: 0.0351
- Valid_ratio range: [0.8626, 0.9910]

### Per-pair outcomes

- city_sim day->day:
  - pass=True, valid_ratio=0.9725, corr=1.0000, norm_mae=0.0000, ds=10, th=0.8
- city_sim day->night:
  - pass=True, valid_ratio=0.8626, corr=0.7319, norm_mae=0.1193, ds=50, th=1.0
- village_sim day->day:
  - pass=True, valid_ratio=0.9910, corr=1.0000, norm_mae=0.0000, ds=10, th=1.0
- village_sim day->winter:
  - pass=True, valid_ratio=0.9552, corr=0.9609, norm_mae=0.0210, ds=50, th=1.0

## 4) Interpretation

- The pipeline is stable and correctly recovers identity matches.
- Appearance change effects are measurable and consistent with expectation.
- More challenging condition gaps selected larger sequence context (ds=50), which aligns with SeqSLAM behavior in harder visual conditions.

## 5) Risks / Caveats

- These results are specific to current route geometry and selected condition pairs.
- Generalization to additional routes or weather profiles requires new runs under the same contract.

## 6) Decision

Phase 0 for sim-worlds is complete and accepted as the frozen baseline protocol.

## 7) Immediate Next Steps

1. Start Phase 1 with any new planned sim-world pairs (if scope expands).
2. Keep this Phase 0 contract unchanged for baseline comparability.
3. If protocol changes are required, create a versioned contract file before re-running benchmarks.
