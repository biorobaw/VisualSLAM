# SeqSLAM Oxford Experiments Progress Report (2026-02-24)

This report summarizes recent SeqSLAM experiments on the Oxford RobotCar dataset, including implementation updates, tuning outcomes, and next steps.

## 1) Objective

The objective was to improve sequence-matching robustness and reporting quality for Oxford-to-Oxford place recognition, especially for challenging cross-condition comparisons.

Two Oxford run pairs were evaluated:

- **Soft pair (easier):** `2014-05-14-13-46-12` vs `2014-05-14-13-50-20`
- **Hard pair (harder):** `2014-05-14-13-46-12` vs `2014-05-19-12-51-39`

## 2) Completed Technical Work

### 2.1 Matching/plot diagnostics improvement

Plotting and diagnostics were updated to distinguish valid and invalid matches explicitly.

- Invalid/filtered assignments are now shown separately in plots.
- Valid and invalid counts are reported directly in outputs.

This prevents misleading interpretation where invalid matches could appear mixed with valid matches.

### 2.2 Tuning pipeline upgrade

The Oxford tuning workflow in `pyseqslam/tune_oxford.py` was extended and improved with:

- Parameter sweeps across `ds`, velocity range, and `Rwindow`
- Threshold sweeps over match quality
- Composite ranking score to balance multiple criteria:

\[
	ext{rank\_score} = 0.45\cdot\text{valid\_ratio} + 0.40\cdot\max(0,\text{corr}) + 0.15\cdot\text{mae\_score}
\]

- Query-length balancing options (`--query-stride`, `--auto-query-stride`)
- Cache fallback handling when legacy `.mat` cache structure fails

## 3) Best Results by Pair

### 3.1 Soft pair result

- **Pair:** `2014-05-14-13-46-12` vs `2014-05-14-13-50-20`
- **Best config:** `ds=10`, `vmin=0.8`, `vmax=1.2`, `Rwindow=10`, `threshold=1.0`
- **Valid matches:** `245 / 284` (**86.27%**)
- **Invalid matches:** `39 / 284`
- **Correlation:** `0.0284`
- **Normalized MAE:** `0.3399`
- **Rank score:** `0.4986`

### 3.2 Hard pair result

- **Pair:** `2014-05-14-13-46-12` vs `2014-05-19-12-51-39`
- **Best config:** `ds=30`, `vmin=0.8`, `vmax=1.2`, `Rwindow=10`, `threshold=1.0`
- **Valid matches:** `1281 / 2105` (**60.86%**)
- **Invalid matches:** `824 / 2105`
- **Correlation:** `0.2742`
- **Normalized MAE:** `0.4226`
- **Rank score:** `0.4701`

## 4) Interpretation of Progress

1. The soft pair achieves higher valid ratio because the runs are closer in conditions.
2. The hard pair is more realistic/challenging; valid ratio is lower, but correlation improved through tuning and sequence balancing.
3. There is still a substantial invalid subset on the hard pair, indicating unresolved ambiguity in confidence scoring and matching stability.

## 5) Main Limitation Identified

The current matching confidence ratio can become unstable in edge cases:

`match = [min_idx + half_ds, min_value / min_value_2nd]`

When the denominator is degenerate/non-finite, quality can become invalid and many matches are filtered. This is the main blocker to further reliability gains.

## 6) Artifacts Produced

For both pairs, the following artifacts were generated:

- `oxford_difference_matrix.png`
- `oxford_matchings.png`
- `oxford_tuning_best_matchings.png`
- `tuning_summary.csv`

Hard pair artifact folder:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-19-12-51-39/`

Soft pair artifact folder:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-14-13-50-20/`

## 7) Next Steps

Prioritized follow-up work:

1. **Stabilize confidence computation** in matching (safe denominator handling + robust confidence margin).
2. **Add temporal consistency post-filtering** to reduce unstable frame-to-frame jumps.
3. **Run focused fine tuning** around the current hard-pair optimum (`ds≈30`, tighter velocity windows, local `Rwindow` sweep).
4. **Expand evaluation over additional Oxford pairs** to validate generalization and avoid overfitting.

## 8) Current Status

- Core tuning infrastructure is implemented and operational.
- Best configurations for both easy and hard Oxford pairs are established.
- Reporting now clearly separates valid vs invalid behavior and soft vs hard pair outcomes.
- Remaining work is primarily algorithmic robustness in confidence scoring and temporal consistency.

Author: Asadbek Nematov
