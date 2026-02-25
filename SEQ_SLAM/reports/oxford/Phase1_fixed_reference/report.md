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

## Next Pair

- `2014-05-14-13-46-12__sun` vs `2014-05-06-13-09-52__clouds_sun`
