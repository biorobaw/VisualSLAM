# Sim-Worlds Directional Follow-up Status Report

Date: 2026-03-28
Protocol: city_village_worlds_directional_followup
Summary source: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_directional_followup/summary.csv

## Run completion

- Planned pairs: 6
- Completed pairs: 6
- tuning_pass: 6/6

## Aggregate metrics

- Average valid_ratio: 0.8123
- Average corr: 0.9424
- Average norm_mae: 0.0268

## Key outcomes

- Same-condition checks remain near-perfect:
  - city night -> city night: rank=0.9876, valid_ratio=0.9725
  - village winter -> village winter: rank=0.9960, valid_ratio=0.9910
- Village cross-season is directionally stable:
  - day -> winter and winter -> day both ~0.9552 valid_ratio
- City cross-condition shows directional asymmetry:
  - day -> night: valid_ratio=0.8626
  - night -> day: valid_ratio=0.1374 (with high corr), indicating a stricter filtering behavior in the selected best setting

## Interpretation

- Directional robustness appears strong for village_sim.
- city_sim requires an additional policy check because correlation alone can look strong while retained valid matches drop sharply in one direction.

## Recommended immediate next action

- Re-rank city_sim directional runs with a stronger valid_ratio requirement (or minimum valid_count gate) and confirm whether the selected best row changes.
