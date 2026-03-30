# Sim-Worlds Comparison: Baseline vs Directional (Gated)

Date: 2026-03-29

## Scope

This report compares:

- Baseline run set: 4-pair protocol in SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv
- Directional follow-up (gated): 6-pair protocol in SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_directional_followup_gated/summary.csv

The directional follow-up uses best-row gating:

- min_valid_ratio = 0.5
- min_valid_count = 100

## Overall completion

- Baseline: 4/4 pairs passed
- Directional (gated): 6/6 pairs passed

## Aggregate comparison

| Set | Pairs | Pass | Avg valid_ratio | Avg corr | Avg norm_mae |
|---|---:|---:|---:|---:|---:|
| Baseline | 4 | 4 | 0.9454 | 0.9232 | 0.0351 |
| Directional (gated) | 6 | 6 | 0.9332 | 0.8139 | 0.0635 |
| Delta (Directional - Baseline) | +2 | +2 | -0.0121 | -0.1093 | +0.0284 |

## Directional follow-up by dataset group

| Dataset group | Avg valid_ratio | Avg corr | Avg norm_mae |
|---|---:|---:|---:|
| city_sim | 0.8993 | 0.6536 | 0.1134 |
| village_sim | 0.9671 | 0.9743 | 0.0136 |

## Key findings

1. Baseline stability remains confirmed by high same-condition quality and full pass rate.
2. Directional gated results are complete and fairer than ungated selection because low-retention rows are not chosen as best.
3. village_sim is directionally robust: high valid ratio, high correlation, low normalized MAE in both directions.
4. city_sim shows stronger directional sensitivity, especially in night to day direction where correlation is much lower despite retained valid matches under gating.
5. The gating policy improved interpretability by converting the earlier city directional artifact into a high-retention comparison.

## Decision

Use the directional gated set as the official directional robustness reference for sim-world reporting.

## Recommended immediate next step

Start the cross-model evaluation block with one pilot trajectory workflow:

1. Freeze trajectory export contract for all SLAM systems (TUM-style fields and coordinate assumptions).
2. Build one converter per model output to the shared format.
3. Run one evo pilot (ATE/RPE) on a selected sim-world pair and publish a first cross-model metrics table.

## Evidence links

- Baseline status: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/phase0_status_report_2026-03-28.md
- Directional gated status: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_directional_followup_gated/status_report_2026-03-28.md
- Baseline summary: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv
- Directional gated summary: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_directional_followup_gated/summary.csv
