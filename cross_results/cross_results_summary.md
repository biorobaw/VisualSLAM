# Cross-Model SLAM Comparison: ORB-SLAM3 vs RatSLAM vs SeqSLAM

**Generated:** 2026-04-25  
**Tool:** `evo_res` (evo toolkit)  
**Models:** ORB-SLAM3 (monocular), RatSLAM, SeqSLAM (proxy place-match evaluation)  

---

## Overview

This folder contains `evo_res` cross-model comparisons across 6 sequences. Oxford and city sim sequences have **3-way** comparisons (ORB-SLAM3 vs RatSLAM vs SeqSLAM). Village sequences have **2-way** comparisons (ORB-SLAM3 vs SeqSLAM — no RatSLAM data available).

Each sub-folder contains:
- `*_3way_comparison.csv` / `*_comparison.csv` — tabular metric summaries
- `*_3way_boxplot_*.png` / `*_boxplot_*.png` — box plots, histograms, violin plots, raw data, and stat summaries

### ⚠️ Important Evaluation Caveat

The three models use **different evaluation paradigms**:
- **ORB-SLAM3** — direct monocular trajectory estimation vs ground truth (Sim(3) aligned where possible)
- **RatSLAM** — experience-map trajectory estimation vs ground truth
- **SeqSLAM** — place-match proxy: matched reference poses looked up from GT → measures *place recognition accuracy*, not trajectory estimation. Zero error on self-match (sanity) is expected.

The evo result zips are in the same format, so `evo_res` can compare them, but the numbers measure fundamentally different capabilities. This should be noted in any publication.

---

## Summary Table — APE (Translation RMSE, meters)

| Sequence | ORB-SLAM3 | RatSLAM | SeqSLAM (proxy) | Notes |
|---|---|---|---|---|
| **Oxford Sunny** | **5.76 m** | 59.35 m | 0.004 m† | Sim(3) aligned; †self-match sanity (expected ≈0) |
| **Oxford Overcast** | **8.86 m** | 63.43 m | 0.12 m† | Sim(3) aligned; †cross-condition proxy |
| **City Day (sim)** | 110.99 m | **15.75 m** | 0.00 m† | Not aligned; †self-match sanity |
| **City Night (sim)** | 117.68 m | **66.21 m** | 117.55 m | Not aligned; SeqSLAM cross-condition match |
| **Village Day (sim)** | **0.30 m** | — | 0.00 m† | Sim(3) aligned; †self-match sanity |
| **Village Winter (sim)** | **2.16 m** | — | 173.79 m | Sim(3) aligned; SeqSLAM cross-condition match |

## Summary Table — RPE (Translation RMSE, meters)

| Sequence | ORB-SLAM3 | RatSLAM | SeqSLAM (proxy) | Notes |
|---|---|---|---|---|
| **Oxford Sunny** | 0.46 m | 0.65 m | **0.002 m**† | †self-match sanity |
| **Oxford Overcast** | 1.02 m | **0.65 m** | 0.09 m† | †cross-condition proxy |
| **City Day (sim)** | 3.30 m | **2.67 m** | 0.00 m† | †self-match sanity |
| **City Night (sim)** | **2.00 m** | 3.10 m | 111.76 m | SeqSLAM cross-condition |
| **Village Day (sim)** | **2.61 m** | — | 0.00 m† | †self-match sanity |
| **Village Winter (sim)** | **7.64 m** | — | 152.11 m | SeqSLAM cross-condition |

> † SeqSLAM self-match (same-condition) results are expected to be near-zero since matched poses come from the same GT trajectory. These serve as sanity checks.

---

## Sequence-by-Sequence Analysis

### 1. Oxford Sunny (2014-05-14-13-46-12) — 3-way

**ORB-SLAM3 dominates** with ATE 5.76 m vs RatSLAM's 59.35 m (10× better). SeqSLAM's self-match proxy shows near-zero error (0.004 m) as expected for same-condition matching.

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 5.76 m | 0.46 m | 210 |
| RatSLAM | 59.35 m | 0.65 m | ~2700 |
| SeqSLAM (proxy) | 0.004 m | 0.002 m | ~3388 |

**Plots:** `oxford_sunny/ape_3way_boxplot_*.png`, `oxford_sunny/rpe_3way_boxplot_*.png`

### 2. Oxford Overcast (2014-06-26-08-53-56) — 3-way

**ORB-SLAM3 wins globally** (8.86 m vs 63.43 m). SeqSLAM's cross-condition proxy (sunny→overcast) achieves 0.12 m APE, demonstrating strong place recognition across lighting conditions on Oxford data.

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 8.86 m | 1.02 m | 358 |
| RatSLAM | 63.43 m | 0.65 m | ~2880 |
| SeqSLAM (proxy) | 0.12 m | 0.09 m | ~2990 |

**Plots:** `oxford_overcast/ape_3way_boxplot_*.png`, `oxford_overcast/rpe_3way_boxplot_*.png`

### 3. City Sim — Day — 3-way

**RatSLAM wins** on APE (15.75 m vs ORB's 110.99 m). SeqSLAM self-match is 0.0 m (sanity). ORB-SLAM3 suffers severe monocular scale drift (planar degeneracy prevents alignment).

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 110.99 m | 3.30 m | 280 |
| RatSLAM | 15.75 m | 2.67 m | ~364 |
| SeqSLAM (proxy) | 0.00 m | 0.00 m | ~364 |

**Plots:** `city_day/ape_3way_boxplot_*.png`, `city_day/rpe_3way_boxplot_*.png`

### 4. City Sim — Night — 3-way

All three models struggle. **RatSLAM best APE** (66.21 m). SeqSLAM's cross-condition match (day→night) yields 117.55 m — similar to ORB-SLAM's 117.68 m — indicating poor place recognition across day/night in sim.

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 117.68 m | 2.00 m | 56 |
| RatSLAM | 66.21 m | 3.10 m | ~364 |
| SeqSLAM (proxy) | 117.55 m | 111.76 m | ~314 |

**Plots:** `city_night/ape_3way_boxplot_*.png`, `city_night/rpe_3way_boxplot_*.png`

### 5. Village Sim — Day — 2-way (ORB-SLAM3 vs SeqSLAM)

**ORB-SLAM3**: 0.30 m APE (excellent, with Sim(3) alignment). SeqSLAM self-match is 0.0 m (sanity).

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 0.30 m | 2.61 m | 26 |
| SeqSLAM (proxy) | 0.00 m | 0.00 m | ~1116 |

**Plots:** `village_day/ape_boxplot_*.png`, `village_day/rpe_boxplot_*.png`

### 6. Village Sim — Winter — 2-way (ORB-SLAM3 vs SeqSLAM)

**ORB-SLAM3 wins** (2.16 m APE vs SeqSLAM's 173.79 m). SeqSLAM's cross-condition match (day→winter) fails dramatically in the village, with very high variance (std=150 m).

| Model | APE RMSE | RPE RMSE | Poses |
|---|---|---|---|
| ORB-SLAM3 | 2.16 m | 7.64 m | 30 |
| SeqSLAM (proxy) | 173.79 m | 152.11 m | ~1066 |

**Plots:** `village_winter/ape_boxplot_*.png`, `village_winter/rpe_boxplot_*.png`

---

## Key Takeaways

1. **ORB-SLAM3 excels on real-world Oxford data** — 5–9 m ATE vs 59–63 m for RatSLAM, benefiting from Sim(3) alignment and rich feature environments.

2. **RatSLAM is more robust in simulation** — ORB-SLAM3's monocular pipeline suffers severe scale drift in Webots sim worlds (planar motion + limited texture).

3. **SeqSLAM proxy evaluation has different semantics** — Self-match (same condition) is expected to be near-zero. Cross-condition results reveal place recognition capability: excellent on Oxford (0.12 m sunny→overcast), but poor in sim worlds for day→night and day→winter.

4. **Condition shift is the hardest challenge** — All models degrade significantly under day→night or summer→winter condition changes in simulation. SeqSLAM and ORB-SLAM both show >100 m ATE for city night cross-condition matching.

5. **Alignment asymmetry** — Oxford results use Sim(3) Umeyama alignment; some sim results are unaligned due to planar degeneracy. Village results are aligned. This should be noted in publication.

6. **Low pose count warning** — ORB-SLAM3 tracked very few poses on some sim sequences (56 for city night, 26–30 for village). Metrics should be interpreted cautiously with small sample sizes.

---

## SeqSLAM Evo Zip Source Mapping

| Sequence | SeqSLAM Zip Source Path |
|---|---|
| Oxford Sunny | `seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-05-14-13-46-12/02_evo_proxy/` |
| Oxford Overcast | `seqslam_full_eval_2026-04-17_run1/oxford/03_pairs/2014-05-14-13-46-12_vs_2014-06-26-08-53-56/02_evo_proxy/` |
| City Day | `seqslam_full_eval_2026-04-17_run1/sim_worlds/03_pairs/city_summer_vs_city_summer/02_evo/outputs/` |
| City Night | `seqslam_full_eval_2026-04-17_run1/sim_worlds/03_pairs/city_summer_vs_city_night/02_evo/outputs/` |
| Village Day | `seqslam_full_eval_2026-04-17_run1/sim_worlds/03_pairs/village_summer_vs_village_summer/02_evo/outputs/` |
| Village Winter | `seqslam_full_eval_2026-04-17_run1/sim_worlds/03_pairs/village_summer_vs_village_winter/02_evo/outputs/` |

---

## File Inventory

```
cross_results/
├── cross_results_summary.md          (this file)
├── oxford_sunny/
│   ├── ape_3way_comparison.csv       (ORB vs RatSLAM vs SeqSLAM)
│   ├── ape_3way_boxplot_*.png        (5 plot types)
│   ├── rpe_3way_comparison.csv
│   ├── rpe_3way_boxplot_*.png
│   ├── ape_comparison.csv            (original 2-way ORB vs RatSLAM)
│   └── ape_boxplot_*.png, rpe_*
├── oxford_overcast/                  (same structure as oxford_sunny)
├── city_day/                         (same structure — 3-way)
├── city_night/                       (same structure — 3-way)
├── village_day/
│   ├── ape_comparison.csv            (2-way: ORB vs SeqSLAM)
│   ├── ape_boxplot_*.png
│   ├── rpe_comparison.csv
│   └── rpe_boxplot_*.png
└── village_winter/                   (same structure as village_day)
```

## Source Data

- **ORB-SLAM3:** `VisualSLAM/ORB_SLAM/results/metrics_summary.csv` — best runs selected by lowest ATE RMSE
- **RatSLAM:** `VisualSLAM/RAT_SLAM/*.zip` — evo result archives from partner
- **SeqSLAM:** `VisualSLAM/SEQ_SLAM/reports/cross_model/seqslam_full_eval_2026-04-17_run1/` — evo proxy result archives
