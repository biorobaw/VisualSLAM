# SeqSLAM Experiment Reports

This directory contains detailed experiment reports organized by dataset.

## Structure

```
reports/
├── README.md                              # This file
├── nordland/
│   └── report.md                         # Nordland dataset experiments
├── oxford/
│   └── Oxford_2014-05-14-13-50-20/       # Specific Oxford run
│       └── report.md                      # Experiment report for this run
└── sim_worlds/
    └── CityVillage_worlds/               # Separate City/Village simulator phase
        ├── summary.csv
        └── report.md
```

## Datasets

### Nordland Railway Dataset
- **Type**: Seasonal traverse (train journey through Norway)
- **Sequences**: Spring vs Winter
- **Environment**: Scenic/natural landscape
- **Location**: [reports/nordland/report.md](nordland/report.md)

### Oxford RobotCar Dataset
- **Type**: Urban driving dataset
- **Runs**: Multiple sequences from different times/weather conditions
- **Environment**: City streets, buildings, intersections
- **Each run has its own folder**: `reports/oxford/<run_name>/report.md`

#### Available Oxford Runs
1. **Oxford_2014-05-14-13-50-20** ✅
   - Camera: Grasshopper 2 Left (mono_left)
   - Date: May 14, 2014, 13:50:20
   - Frames: 284 images
   - Status: Completed

### City/Village Simulator Worlds (Separate from Oxford)
- **Type**: Simulator driving datasets (city and village worlds)
- **Comparisons**:
    - city day vs city day
    - city day vs city night
    - village day vs village day
    - village day vs village winter
- **Location**: `reports/sim_worlds/CityVillage_worlds/`

## Results Location

Corresponding results are organized in `pyseqslam/results/`:

```
pyseqslam/results/
├── nordland/
│   ├── difference_matrix_ds10.png
│   ├── difference_matrix_ds20.png
│   ├── difference_matrix_ds30.png
│   ├── matchings_ds10.png
│   ├── matchings_ds20.png
│   └── matchings_ds30.png
└── oxford/
    └── Oxford_2014-05-14-13-50-20/
        ├── oxford_difference_matrix.png
        └── oxford_matchings.png
```

## Quick Links

- [Nordland Report](nordland/report.md)
- [Oxford 2014-05-14-13-50-20 Report](oxford/Oxford_2014-05-14-13-50-20/report.md)
- [Oxford SeqSLAM Research To-Do](oxford/research_todo_seqslam.md)
- [Oxford Phase 1 Fixed-Reference Report](oxford/Phase1_fixed_reference/report.md)
- [City/Village Simulator Tuning Report](sim_worlds/CityVillage_worlds/report.md)

## Adding New Experiments

When testing new datasets:

1. Create a new folder: `reports/<dataset>/<specific_run>/`
2. Create `report.md` with experiment details
3. Organize results: `pyseqslam/results/<dataset>/<specific_run>/`
4. Update this README with links

## Report Template

Each report should include:
- Dataset information (name, size, source)
- Experiment configuration (parameters used)
- Results (metrics, visualizations)
- Key findings and observations
- Code modifications (if any)
- Next steps

## Comparison

| Dataset | Environment | Frames | Match Rate | Processing Time |
|---------|-------------|--------|------------|-----------------|
| Nordland | Scenic | 357 (sampled) | TBD | ~60s (first run) |
| Oxford 2014-05-14 | Urban | 284 | 38.7% | 3.66s |
