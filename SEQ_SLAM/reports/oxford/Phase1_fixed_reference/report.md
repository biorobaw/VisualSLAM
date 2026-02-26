# Oxford Phase 1 Report — Fixed Reference

## Scope

- Phase: 1 (fixed-reference)
- Total planned comparisons: 10
- Reference run: `2014-05-14-13-46-12__sun`
- Status: in progress

## Environment Notes

- Python execution now uses project venv:
  - `/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python`
- Reason: system/Homebrew Python was missing modules and blocked global pip installs.

## Run 001

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-05-06-12-54-54__clouds_sun`
- Query stride: 2 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-05-06-12-54-54__clouds_sun \
  --auto-query-stride
```

Best result:

- `ds=10`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1219/1937` (`62.93%`)
- Corr: `0.2534`
- MAE: `872.97` frames
- Normalized MAE: `0.4133`
- DD build/load time: `43.28s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-12-54-54__clouds_sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-12-54-54__clouds_sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned full ranked results.

## Experiment — Sun Reference vs Clouds/Sun Query (2014-05-06-13-09-52)

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-05-06-13-09-52__clouds_sun`
- Query stride: 2 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-05-06-13-09-52__clouds_sun \
  --auto-query-stride
```

Best result:

- `ds=20`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1197/1907` (`62.77%`)
- Corr: `0.2455`
- MAE: `904.58` frames
- Normalized MAE: `0.4283`
- DD build/load time: `43.19s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-09-52__clouds_sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-09-52__clouds_sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Experiment — Sun Reference vs Clouds/Poor-GPS Query (2014-05-06-13-14-58)

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-05-06-13-14-58__clouds_poor_gps_sun`
- Query stride: 1 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-05-06-13-14-58__clouds_poor_gps_sun \
  --auto-query-stride
```

Best result:

- `ds=20`, `vmin=0.30`, `vmax=2.00`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1262/2048` (`61.62%`)
- Corr: `0.2368`
- MAE: `861.89` frames
- Normalized MAE: `0.4081`
- DD build/load time: `46.65s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-14-58__clouds_poor_gps_sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-06-13-14-58__clouds_poor_gps_sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Experiment — Sun Reference vs Sun Query (2014-05-14-13-50-20)

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-05-14-13-50-20__sun`
- Query stride: 1 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-05-14-13-50-20__sun \
  --auto-query-stride
```

Best result:

- `ds=10`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `245/284` (`86.27%`)
- Corr: `0.0284`
- MAE: `717.82` frames
- Normalized MAE: `0.3399`
- DD build/load time: `23.27s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-14-13-50-20__sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-14-13-50-20__sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Experiment — Sun Reference vs Poor-GPS/Sun Query (2014-05-19-12-51-39)

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-05-19-12-51-39__poor_gps_sun`
- Query stride: 3 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-05-19-12-51-39__poor_gps_sun \
  --auto-query-stride
```

Best result:

- `ds=30`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1281/2105` (`60.86%`)
- Corr: `0.2742`
- MAE: `892.49` frames
- Normalized MAE: `0.4226`
- DD build/load time: `50.58s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-19-12-51-39__poor_gps_sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-05-19-12-51-39__poor_gps_sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Experiment — Sun Reference vs Sun Query (2014-06-23-15-14-44)

- Date: 2026-02-25
- Pair: `2014-05-14-13-46-12__sun` vs `2014-06-23-15-14-44__sun`
- Query stride: 1 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-06-23-15-14-44__sun \
  --auto-query-stride
```

Best result:

- `ds=10`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1538/2674` (`57.52%`)
- Corr: `0.2860`
- MAE: `1000.26` frames
- Normalized MAE: `0.4736`
- DD build/load time: `60.45s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-06-23-15-14-44__sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-06-23-15-14-44__sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Experiment — Sun Reference vs Sun Query (2014-06-23-15-36-04)

- Date: 2026-02-26
- Pair: `2014-05-14-13-46-12__sun` vs `2014-06-23-15-36-04__sun`
- Query stride: 1 (auto)

Command:

```bash
/Users/asadbeknematov/Desktop/Projects/VisualSLAM/.venv/bin/python -u tune_oxford.py \
  --reference-run 2014-05-14-13-46-12__sun \
  --query-run 2014-06-23-15-36-04__sun \
  --auto-query-stride
```

Best result:

- `ds=30`, `vmin=0.80`, `vmax=1.20`, `Rwindow=10`, `threshold=1.00`
- Valid matches: `1471/2545` (`57.80%`)
- Corr: `0.2733`
- MAE: `952.70` frames
- Normalized MAE: `0.4511`
- DD build/load time: `56.51s`

Artifacts:

- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-06-23-15-36-04__sun/tuning_summary.csv`
- `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12__sun_vs_2014-06-23-15-36-04__sun/oxford_tuning_best_matchings.png`

Observations:

- Automatic cache load again attempted old `.mat` layout and fell back to recomputation.
- Matcher printed one runtime warning (`invalid value encountered in scalar divide`) but returned complete ranked results.

## Next Pair

- `2014-05-14-13-46-12__sun` vs `2014-06-23-15-41-25__sun`
