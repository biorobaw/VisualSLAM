# Sim-Worlds Directional Follow-up Gated Status

Date: 2026-03-28
Protocol: city_village_worlds_directional_followup_gated
Summary source: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_directional_followup_gated/summary.csv

## Completion

- Planned pairs: 6
- Completed pairs: 6
- tuning_pass: 6/6

## Gate settings

- min_valid_ratio: 0.5
- min_valid_count: 100

## Main result

The full directional follow-up now uses a consistent valid-match gate for best-row selection across all pairs.

This prevents low-retention rows from being selected as "best" solely due to high correlation and produces more stable directional comparisons.

## Next recommendation

Use this gated directional report as the official directional baseline for upcoming comparison writeups and commit these artifacts together with the gating script update.
