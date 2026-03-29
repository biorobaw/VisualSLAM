# City Directional Gated Follow-up Status

Date: 2026-03-28
Protocol: city_village_worlds_city_directional_gated
Summary source: SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_city_directional_gated/summary.csv

## Completion

- Planned pairs: 3
- Completed pairs: 3
- tuning_pass: 3/3

## Gate settings used

- min_valid_ratio: 0.5
- min_valid_count: 100

## Result highlights

- day -> night:
  - valid_ratio=0.8626, valid_count=314, corr=0.7319, rank=0.8130
- night -> day:
  - valid_ratio=0.8626, valid_count=314, corr=0.2288, rank=0.5966
- night -> night sanity:
  - valid_ratio=0.9725, valid_count=354, corr=1.0000, rank=0.9876

## Main outcome

The gate removed the earlier low-retention selection for night -> day and forced a high-retention best row. Directional asymmetry still exists, but it is now reflected as lower correlation/score rather than a tiny valid match set.

## Recommended next action

Apply the same gate settings to the full 6-pair directional follow-up and regenerate its summary/report so all directional results use one consistent selection policy.
