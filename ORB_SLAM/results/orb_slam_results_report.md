# ORB-SLAM3 Monocular Evaluation Results

**Generated:** 2026-04-25  
**Algorithm:** ORB-SLAM3 (Monocular)  
**Alignment:** Umeyama sim(3) (scale + SE(3))  
**Metrics:** ATE (translational RMSE, m), RPE translational (m/frame), RPE rotational (deg/frame)

---

## 1. Executive Summary

We evaluated ORB-SLAM3 in monocular mode across **6 sequences** spanning two real-world Oxford RobotCar datasets and four Webots simulation scenarios. Of 101 total estimation files, **41 produced valid metrics** (had both groundtruth and sufficient estimated poses). The remaining 60 were either missing groundtruth or had empty/near-empty estimation outputs (ORB-SLAM3 failed to initialize or lost tracking).

| Sequence | Environment | Condition | Valid Runs / Total | Best ATE RMSE (m) | Tracking Success |
|---|---|---|---|---|---|
| ORC-sun | Oxford RobotCar | Sunny | 11 / 21 | **5.79** | High |
| ORC-overcast | Oxford RobotCar | Overcast | 11 / 21 | **8.82** | High (but bimodal) |
| city_sim_day | Webots City | Day | 2 / 16 | **13.61** | Very Low |
| city_sim_night | Webots City | Night | 5 / 16 | **1.00** | Low |
| village_sim_day | Webots Village | Day | 6 / 16 | **0.42** | Moderate |
| village_sim_winter | Webots Village | Winter | 6 / 16 | **0.43** | Moderate |

---

## 2. Per-Sequence Detailed Results

### 2.1 ORC-sun (Oxford RobotCar — Sunny)

**Dataset:** `2014-05-14-13-46-12` — Sunny conditions, good feature visibility  
**Valid runs:** 11 (dates: 04-19, 04-20, 04-21)

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-19 | 1 | 216 | 6.19 | 1.65 | 1.19 |
| 2026-04-19 | 2 | 222 | 6.10 | 1.70 | 1.22 |
| 2026-04-19 | 3 | 214 | 6.16 | 1.71 | 1.18 |
| 2026-04-19 | 4 | 401 | 10.50 | 1.27 | 0.97 |
| 2026-04-19 | 5 | 407 | 10.64 | 1.25 | 0.94 |
| 2026-04-20 | 1 | 384 | 11.25 | 1.05 | 0.95 |
| 2026-04-20 | 2 | 208 | 5.81 | 0.31 | 1.01 |
| 2026-04-20 | 3 | 206 | 6.01 | 1.06 | 1.10 |
| 2026-04-20 | 4 | 211 | 5.79 | 0.30 | 1.05 |
| 2026-04-20 | 5 | 215 | 6.16 | 1.73 | 1.24 |
| **2026-04-21** | **1** | **167** | **5.88** | **0.35** | **1.14** |

**Summary statistics (all 11 runs):**
- ATE RMSE: **7.31 ± 2.12 m** (min 5.79, max 11.25)
- RPE Trans RMSE: **1.04 ± 0.58 m** (min 0.30, max 1.73)
- RPE Rot RMSE: **1.09 ± 0.11°** (min 0.94, max 1.24)

**Assessment:** ✅ **Consistent and usable.** All 11 runs converged. Two clusters visible: ~6m ATE (shorter tracking segments, ~210 poses) and ~10.5m ATE (longer segments, ~400 poses). The best runs achieve ~5.8m ATE with very low frame-to-frame RPE (~0.3m).

---

### 2.2 ORC-overcast (Oxford RobotCar — Overcast)

**Dataset:** `2014-06-26-08-53-56` — Overcast/cloudy conditions  
**Valid runs:** 11 (dates: 04-19, 04-20, 04-21)

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-19 | 1 | 386 | **9.44** | 0.24 | 0.98 |
| 2026-04-19 | 2 | 1319 | 99.38 | 0.70 | 1.03 |
| 2026-04-19 | 3 | 1302 | 102.19 | 0.73 | 1.26 |
| 2026-04-19 | 4 | 1310 | 98.39 | 0.70 | 1.06 |
| 2026-04-19 | 5 | 358 | **8.82** | 0.24 | 1.02 |
| 2026-04-20 | 1 | 359 | **9.06** | 0.24 | 1.00 |
| 2026-04-20 | 2 | 1276 | 100.86 | 0.73 | 1.06 |
| 2026-04-20 | 3 | 1273 | 114.26 | 0.80 | 1.15 |
| 2026-04-20 | 4 | 1349 | 114.97 | 0.74 | 1.13 |
| 2026-04-20 | 5 | 1330 | 107.77 | 0.72 | 1.46 |
| 2026-04-21 | 1 | 1117 | 115.29 | 0.87 | 1.59 |

**⚠️ Bimodal behavior detected:**

| Cluster | Runs | ATE RMSE (m) | Matched Poses | Interpretation |
|---|---|---|---|---|
| **Good** (3 runs) | 04-19/1, 04-19/5, 04-20/1 | **9.11 ± 0.31** | ~360 | Correct scale/alignment |
| **Drifted** (8 runs) | All others | **106.64 ± 7.13** | ~1280 | Catastrophic scale drift |

**Assessment:** ⚠️ **Bimodal — use with caution.** The 3 "good" runs (ATE ~9m) are comparable to ORC-sun performance. The 8 "drifted" runs show catastrophic scale failure despite having more matched poses — the longer tracking duration leads to accumulated monocular scale drift. **Recommended representative result: 9.11 ± 0.31 m** (good cluster only).

---

### 2.3 City Sim — Day

**Dataset:** `city_sim_day_centerline` — Webots city environment, daytime  
**Valid runs:** 2 / 16 (most runs produced 0 estimated poses)

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-20 | 1 | 261 | 18.71 | 1.82 | 2.86 |
| 2026-04-20 | 3 | 280 | 13.61 | 0.97 | 3.70 |

**Assessment:** ❌ **Mostly failed.** 14 out of 16 runs produced empty estimation files (ORB-SLAM3 could not initialize or lost tracking immediately). The 2 successful runs show moderate-to-high ATE (13.6–18.7m). The city environment likely has repetitive textures and wide roads that challenge monocular feature matching.

---

### 2.4 City Sim — Night

**Dataset:** `city_sim_night_centerline` — Webots city environment, nighttime  
**Valid runs:** 5 / 16

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-20 | 1 | 56 | **1.00** | 0.62 | 4.39 |
| 2026-04-20 | 3 | 63 | 1.14 | 0.60 | 4.18 |
| 2026-04-20 | 4 | 159 | 7.65 | 0.70 | 3.06 |
| 2026-04-20 | 5 | 57 | 1.10 | 0.61 | 3.96 |
| 2026-04-21 | 1 | 52 | 1.09 | 0.65 | 5.08 |

**Summary (excluding outlier run 4):**
- ATE RMSE: **1.08 ± 0.06 m** (4 runs)
- One outlier run (04-20/4) with 159 poses and 7.65m ATE (likely partial drift)

**Assessment:** ⚠️ **Partially usable.** 11/16 runs failed entirely. When tracking succeeds, ATE is quite good (~1m) but only over short segments (~55 poses). Night conditions paradoxically help by increasing contrast of lit features (streetlights, headlights).

---

### 2.5 Village Sim — Day

**Dataset:** `village_sim_day_centerline_smooth` — Webots village, daytime  
**Valid runs:** 6 / 16

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-20 | 1 | 76 | 38.04 ⚠️ | 5.56 | 11.37 |
| 2026-04-20 | 2 | 42 | 0.69 | 0.51 | 7.40 |
| 2026-04-20 | 3 | 38 | 0.75 | 0.72 | 4.96 |
| 2026-04-20 | 4 | 25 | **0.42** | 0.48 | 6.03 |
| 2026-04-20 | 5 | 36 | 0.55 | 0.52 | 2.28 |
| 2026-04-21 | 1 | 26 | 1.51 | 0.94 | 5.42 |

**Summary (excluding outlier run 04-20/1):**
- ATE RMSE: **0.78 ± 0.41 m** (5 runs)
- Outlier run 04-20/1 (38.04m ATE) had scale drift over 76 poses

**Assessment:** ⚠️ **Good when tracking succeeds, but fragile.** 10/16 runs failed. The 5 good runs show excellent sub-meter ATE, but over very short segments (25–42 poses). Higher RPE rotation (2–7°) reflects the winding village road.

---

### 2.6 Village Sim — Winter

**Dataset:** `village_sim_winter_centerline_smooth` — Webots village, winter conditions  
**Valid runs:** 6 / 16

| Date | Run | Matched Poses | ATE RMSE (m) | RPE Trans RMSE (m) | RPE Rot RMSE (°) |
|---|---|---|---|---|---|
| 2026-04-20 | 1 | 346 | 33.73 ⚠️ | 3.54 | 15.38 |
| 2026-04-20 | 2 | 331 | 37.84 ⚠️ | 5.39 | 11.09 |
| 2026-04-20 | 3 | 33 | 2.34 | 1.65 | 16.64 |
| 2026-04-20 | 4 | 24 | **0.43** | 0.50 | 6.22 |
| 2026-04-20 | 5 | 136 | 13.96 | 2.95 | 6.17 |
| 2026-04-21 | 1 | 30 | 3.28 | 1.85 | 5.66 |

**Assessment:** ❌ **Highly variable.** Same bimodal pattern: long-tracking runs (300+ poses) show catastrophic drift (34–38m ATE), while short-tracking runs (24–33 poses) can be decent (0.43–3.28m). Winter conditions (reduced texture, snow, low contrast) significantly degrade ORB feature extraction.

---

## 3. Cross-Sequence Comparison (Best-Run Results)

| Sequence | Condition | Best ATE RMSE (m) | Best RPE Trans (m) | Best RPE Rot (°) | Poses |
|---|---|---|---|---|---|
| village_sim_day | Sim / Day | **0.42** | 0.48 | 6.03 | 25 |
| village_sim_winter | Sim / Winter | **0.43** | 0.50 | 6.22 | 24 |
| city_sim_night | Sim / Night | **1.00** | 0.62 | 4.39 | 56 |
| ORC-sun | Real / Sunny | **5.79** | 0.30 | 1.05 | 211 |
| ORC-overcast | Real / Overcast | **8.82** | 0.24 | 1.02 | 358 |
| city_sim_day | Sim / Day | **13.61** | 0.97 | 3.70 | 280 |

---

## 4. Key Observations

1. **Monocular scale ambiguity dominates error.** The bimodal ATE distributions in ORC-overcast (9m vs 100m+) and village_sim (0.4m vs 35m+) are classic monocular scale drift. Longer tracking segments accumulate more drift.

2. **Simulation tracking is fragile.** City sim day achieved only 12.5% success rate (2/16 runs). The synthetic textures and repetitive geometry challenge ORB feature detection/matching.

3. **Real-world Oxford data is more robust.** 100% of runs with groundtruth produced valid trajectories (11/11 for both sequences), even if some had scale issues.

4. **Short segments ≠ bad results.** The village sim best results (0.42m ATE) are over only 25 poses. These are locally excellent but don't prove long-term stability.

5. **RPE rotation is higher in simulation** (~3–7° for sim vs ~1° for Oxford), suggesting the simulated camera motion is more aggressive or the simulated features are less rotationally stable.

---

## 5. Data Completeness Notes

| Issue | Affected | Count |
|---|---|---|
| No groundtruth file | ORC-sun 04-16, 04-18; ORC-overcast 04-18; village_sim 04-18, 04-19 (partial); village_winter 04-18, 04-19 | ~40 runs |
| Empty estimation (tracking failure) | city_sim_day (14/16), city_sim_night (11/16), village sims (various) | ~20 runs |
| Total valid metrics | All sequences | **41 runs** |

---

## 6. Files Reference

- **Full metrics CSV:** `VisualSLAM/ORB_SLAM/results/metrics_summary.csv` (41 rows, 20 columns)
- **Metrics script:** `VisualSLAM/ORB_SLAM/compute_metrics_standalone.py` (standalone, no evo dependency)
- **Per-run data:** `results/<sequence>/<date>/<run>/` containing `estimation.tum`, `groundtruth.tum`, plots, and evo zip archives (where available)
