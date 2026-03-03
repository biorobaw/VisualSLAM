# City/Village Simulator Tuning Report

## Project narrative (what I did)

### 1) Built two Webots worlds with controlled condition changes

I added and used two dedicated simulator environments in Webots:

- **City world** with two conditions:
  - day
  - night
- **Village world** with two conditions:
  - summer/day
  - winter

World references:
- City day: [Simulator/Webots/worlds/city/city.wbt](Simulator/Webots/worlds/city/city.wbt)
- City night: [Simulator/Webots/worlds/city/city_night.wbt](Simulator/Webots/worlds/city/city_night.wbt)
- Village day/summer: [Simulator/Webots/worlds/village/village.wbt](Simulator/Webots/worlds/village/village.wbt)
- Village winter: [Simulator/Webots/worlds/village/village_winter.wbt](Simulator/Webots/worlds/village/village_winter.wbt)
- Webots setup and collection guide: [Simulator/Webots/README.md](Simulator/Webots/README.md)

I kept route geometry consistent per world so that changes in matching quality mainly reflect visual appearance change (lighting/season), not route mismatch.

### 2) Ran path traversal and collected camera data

I executed path traversal in Webots and recorded image streams from:

- front camera → [SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_front](SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_front), [SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_front](SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_front), [SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_front](SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_front), [SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_front](SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_front)
- side cameras (`mono_side`, with SeqSLAM-compatible stream in `mono_left`) → [SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_side](SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_side), [SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_left](SEQ_SLAM/datasets/city_sim/city_sim_day_centerline/mono_left), [SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_side](SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_side), [SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_left](SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/mono_left), [SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_side](SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_side), [SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_left](SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth/mono_left), [SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_side](SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_side), [SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_left](SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth/mono_left)

Collection workflow reference (including controller and camera-mode usage): [Simulator/Webots/README.md](Simulator/Webots/README.md)

This gave me paired traversals under different environmental conditions while preserving the same route intention.

### 3) Packaged simulator outputs into Oxford-like dataset format

To reuse the existing SeqSLAM pipeline, I organized the collected frames in an Oxford-style structure:

- run-specific folders per condition
- timestamp-ordered `.png` images
- `mono_left` folder layout consumed by SeqSLAM scripts

Dataset references used in this report:
- City day: [SEQ_SLAM/datasets/city_sim/city_sim_day_centerline](SEQ_SLAM/datasets/city_sim/city_sim_day_centerline)
- City night: [SEQ_SLAM/datasets/city_sim/city_sim_night_centerline](SEQ_SLAM/datasets/city_sim/city_sim_night_centerline)
- Village day: [SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth](SEQ_SLAM/datasets/village_sim/village_sim_day_centerline_smooth)
- Village winter: [SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth](SEQ_SLAM/datasets/village_sim/village_sim_winter_centerline_smooth)

This made simulator runs directly compatible with the same loading/preprocessing/tuning scripts I used for Oxford experiments.

## Evaluated comparisons

- city day vs city day
- city day vs city night
- village day vs village day
- village day vs village winter

## Validation strategy (sanity check first)

Before testing cross-condition robustness, I first compared each condition against itself:

- **city day vs city day**
- **village day vs village day**

Why this step matters:

- verifies indexing, preprocessing, and matching logic
- confirms the pipeline can recover near-perfect alignment on identical traversals
- reduces risk of attributing pipeline bugs to condition-change difficulty

After this sanity check, I evaluated the harder pairs:

- **city day vs city night**
- **village day vs village winter**

## Tuning procedure

For each pair I:

1. Built/loaded preprocessing outputs and contrast-enhanced difference matrix.
2. Swept matching hyperparameters:
   - `ds` (sequence length)
   - velocity bounds (`vmin`, `vmax`)
   - `Rwindow`
3. Swept quality `threshold` values over each matching run.
4. Computed metrics (`valid_ratio`, `corr`, `norm_mae`, etc.) and ranked candidates.
5. Saved per-pair outputs (`tuning_summary.csv`, best matching plot).

Tuning script reference: [SEQ_SLAM/pyseqslam/tune_sim_worlds.py](SEQ_SLAM/pyseqslam/tune_sim_worlds.py)

## Command

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_sim_worlds.py --auto-query-stride --no-cache
```

## Outcome

- Tunings passed: **4/4**

Report summary table source: [SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv](SEQ_SLAM/reports/sim_worlds/CityVillage_worlds/summary.csv)

### High-level observations

- Same-condition comparisons were near-perfect, confirming correct pipeline behavior.
- Cross-condition comparisons stayed strong but showed expected degradation from appearance shifts.
- Harder pairs selected larger sequence context (`ds=50`), consistent with SeqSLAM robustness behavior under stronger visual change.

Per-pair tuning outputs (root): [SEQ_SLAM/pyseqslam/results/sim_worlds](SEQ_SLAM/pyseqslam/results/sim_worlds)

## Per-pair best tuning summary

| Dataset | Reference | Query | Pass | Rank | Valid Ratio | Corr | Norm MAE | Best Params |
|---|---|---|---:|---:|---:|---:|---:|---|
| city_sim | city_sim_day_centerline | city_sim_day_centerline | True | 0.9876 | 0.9725 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=0.80 |
| city_sim | city_sim_day_centerline | city_sim_night_centerline | True | 0.8130 | 0.8626 | 0.7319 | 0.1193 | ds=50, v=(0.80,1.20), R=10, th=1.00 |
| village_sim | village_sim_day_centerline_smooth | village_sim_day_centerline_smooth | True | 0.9960 | 0.9910 | 1.0000 | 0.0000 | ds=10, v=(0.80,1.20), R=10, th=1.00 |
| village_sim | village_sim_day_centerline_smooth | village_sim_winter_centerline_smooth | True | 0.9611 | 0.9552 | 0.9609 | 0.0210 | ds=50, v=(0.80,1.20), R=10, th=1.00 |

## Artifact index

- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_day_centerline/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_day_centerline/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_night_centerline/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/city_sim/city_sim_city_sim_day_centerline_vs_city_sim_night_centerline/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_day_centerline_smooth/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_day_centerline_smooth/sim_worlds_tuning_best_matchings.png
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth/tuning_summary.csv
- SEQ_SLAM/pyseqslam/results/sim_worlds/village_sim/village_sim_village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth/sim_worlds_tuning_best_matchings.png
