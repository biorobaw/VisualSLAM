# Next Step Runbook (Sim Worlds)

This runbook executes the next evaluation batch using a pair list CSV and writes results to a dedicated report subfolder.

## 1) Prepare pair list

Edit this file with desired pairs:

- SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/next_pairs_template.csv

Required columns:

- dataset_group
- reference_run
- query_run

## 2) Run tuning with frozen protocol settings

From SEQ_SLAM/pyseqslam:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py \
  --pairs-csv ../reports/sim_worlds/CityVillage_worlds/next_pairs_template.csv \
  --protocol-label city_village_worlds_followup \
  --report-subdir CityVillage_worlds_followup \
  --auto-query-stride \
  --no-cache
```

## 3) Expected outputs

- Summary table:
  - SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_followup/summary.csv
- Batch report:
  - SEQ_SLAM/reports/sim_worlds/CityVillage_worlds_followup/report.md
- Per-pair tuning outputs:
  - SEQ_SLAM/pyseqslam/results/sim_worlds/<dataset_group>/<pair_dir>/

## 4) Acceptance checks

- Every planned pair appears in summary.csv.
- tuning_pass is True for accepted rows.
- Each row has a valid tuning_summary_csv and best_plot path.

## 5) Reporting update

After run completion, summarize:

- total pairs
- passed pairs
- average valid_ratio
- average corr
- average norm_mae
- best and worst pair by rank_score
