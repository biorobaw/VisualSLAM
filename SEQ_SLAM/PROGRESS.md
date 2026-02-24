# SeqSLAM Progress Summary

## What I've Done

### 1. ✅ Got the Pipeline Running
- Downloaded Nordland dataset (446MB, spring/winter sequences)
- Fixed Python 2→3 compatibility issues
- Demo runs successfully on macOS with Python 3.14

### 2. ✅ Generated the Difference Matrix Plot
**What it shows**: Heatmap of image similarity between spring and winter sequences

**Why it matters**: This is SeqSLAM's core - it shows how the algorithm compares every frame from one sequence against every frame from the other sequence. You should see diagonal-ish structure where similar places align.

**Files generated**:
- `results/nordland/difference_matrix_ds10.png`
- `results/nordland/difference_matrix_ds20.png`  
- `results/nordland/difference_matrix_ds30.png`

The darker regions show better matches (lower difference = more similar).

### 3. ✅ Tuned Sequence Length Parameter

**Parameter**: `params.matching.ds` (sequence length)
- **ds=10** (default): Baseline performance
- **ds=20**: Moderate sequence length
- **ds=30**: Longer sequence context

**What to look for**: 
- In the matchings plot, you want a rough diagonal, not a flat line at y≈0
- Longer sequences (higher ds) give more robustness but require more computation
- Check `results/nordland/matchings_ds*.png` to compare

**Files generated**:
- `results/nordland/matchings_ds10.png` 
- `results/nordland/matchings_ds20.png`
- `results/nordland/matchings_ds30.png`

### 4. ✅ Tested on Oxford RobotCar Dataset

**Dataset**: Oxford_2014-05-14-13-50-20  
**Camera**: Grasshopper 2 - Left (mono_left)  
**Frames**: 284 images (1024×1024 grayscale)  
**Split**: First 142 vs Last 142 frames  
**Results**: 38.7% match rate (55/142 frames) in 3.66 seconds

**Key modifications**:
- Added grayscale image support (Oxford images already mono)
- Fixed image resizing (1024×1024 → 64×32)
- Created organized folder structure for results

**Files generated**:
- `results/oxford/Oxford_2014-05-14-13-50-20/oxford_difference_matrix.png`
- `results/oxford/Oxford_2014-05-14-13-50-20/oxford_matchings.png`

## Key Points for Presentation

> **"SeqSLAM is sequence-based place recognition, not full SLAM."**
> 
> **"I got the pipeline running on Nordland and Oxford datasets."**
> 
> **"Nordland shows strong seasonal matching, Oxford shows 38.7% match rate in urban environment."**
> 
> **"The difference matrix is computed once and reused - the sequence length parameter only affects final matching."**

## Technical Details

### SeqSLAM Algorithm Overview
1. **Preprocessing**: Convert images to grayscale, resize to 64×32, patch normalization
2. **Difference Matrix**: Compute pairwise differences between all frames from two sequences
3. **Contrast Enhancement**: Apply local contrast enhancement to highlight structure
4. **Sequence Matching**: Find best-matching sequences using dynamic programming with length `ds`

### Key Parameters
- `imageSkip = 100`: Use every 100th frame (Nordland only)
- `matching.ds`: Sequence length (tunable parameter)
- `matching.vmin = 0.8`: Minimum velocity constraint
- `contrastEnhancement.R = 10`: Contrast enhancement window

### Datasets
- **Nordland**: Train journey in Norway filmed in 4 seasons
  - Using: Spring vs Winter (extreme appearance change)
  - Frames: ~35,000 frames per sequence, using every 100th frame = 357 frames
  
- **Oxford RobotCar**: Urban driving dataset
  - Run: Oxford_2014-05-14-13-50-20
  - Camera: Grasshopper 2 Left (mono_left)
  - Frames: 284 images at 1024×1024 (resized to 64×32)

## Repository Organization

```
pySeqSLAM/
├── reports/                              # Experiment reports
│   ├── nordland/report.md               # Nordland experiments
│   └── oxford/
│       └── Oxford_2014-05-14-13-50-20/
│           └── report.md                 # Oxford experiments
├── pyseqslam/
│   ├── results/                          # Organized results
│   │   ├── nordland/                     # Nordland visualizations
│   │   └── oxford/
│   │       └── Oxford_2014-05-14-13-50-20/  # Oxford visualizations
│   ├── run_experiments.py                # Nordland batch experiments
│   └── run_oxford.py                     # Oxford experiments
└── datasets/                             # Not in Git (local only)
    ├── nordland/64x32-grayscale-1fps/
    └── Oxford_2014-05-14-13-50-20/
```

## Next Steps

1. ✅ Generate difference matrix visualization
2. ✅ Tune sequence length parameter  
3. ✅ Test on Oxford RobotCar dataset
4. ⬜ Test on multiple Oxford runs (different weather/times)
5. ⬜ Compare performance metrics (precision-recall)
6. ⬜ Tune parameters specifically for urban environments

## How to Run

```bash
cd pyseqslam

# Nordland batch experiments with multiple sequence lengths
python run_experiments.py

# Oxford RobotCar experiment
python run_oxford.py
```

## References

- [SeqSLAM Paper (Milford & Wyeth, 2012)](https://ieeexplore.ieee.org/document/6224623)
- [Original OpenSeqSLAM (MATLAB)](http://www.tu-chemnitz.de/etit/proaut/mitarbeiter/niko.html)
- [Nordland Dataset](https://nrkbeta.no/2013/01/15/nordlandsbanen-minute-by-minute-season-by-season/)
- [Oxford RobotCar Dataset](https://robotcar-dataset.robots.ox.ac.uk/)
