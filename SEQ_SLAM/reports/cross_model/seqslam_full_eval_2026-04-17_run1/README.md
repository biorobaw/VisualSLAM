# SeqSLAM Full Evaluation Bundle

Run label: `2026-04-17_run1`

## Layout

- `inputs/`: pair lists used for the run.
- `logs/`: stage-level command logs.
- `sim_worlds/`: full sim-world tuning + evo bundle ready for cross-model comparison.
- `oxford/`: Oxford tuning bundle. `evo` is intentionally skipped there because trajectory ground truth is not present in the current Oxford dataset folders.

## Protocol Summary

- Sim-world camera: `mono_front`
- Oxford image path: `stereo/centre`
- Shared sim-world `evo` policy: raw XY, no alignment, no scale correction, `trans_part` / `angle_deg`, `plot_mode xy`

## Notes

- Sim-world results were also written into the shared cross-model sanity and benchmark CSVs.
- Oxford results are tuning-only in this bundle until trajectory ground truth is added.

## Key Reports

- `sim_worlds/README.md`
- `oxford/01_batch/report.md`