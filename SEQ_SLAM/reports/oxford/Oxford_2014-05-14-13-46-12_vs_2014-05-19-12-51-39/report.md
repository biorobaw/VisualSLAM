# SeqSLAM Experiments: Oxford RobotCar Dataset

## Dataset Pair

**Reference Run**: 2014-05-14-13-46-12 (mono_left)  
**Query Run**: 2014-05-19-12-51-39 (mono_left)  
**Location**: Oxford, UK (city center)  
**Camera**: Grasshopper 2 - Left (mono_left)  

## Split Strategy

This experiment uses two different dates to evaluate matching under changed conditions:

- Reference: 2014-05-14-13-46-12
- Query: 2014-05-19-12-51-39

## Configuration

```python
params.DO_RESIZE = 1
params.DO_GRAYLEVEL = 1
params.DO_PATCHNORMALIZATION = 1
params.matching.ds = 10
params.matching.vmin = 0.8
params.matching.vmax = 1.2
params.matching.Rwindow = 10
params.contrastEnhancement.R = 10
```

## Results

- **Processing Time**: 1663.11 seconds
- **Reference Frames**: 2113
- **Query Frames**: 6314
- **Valid Matches**: 3588 / 6314 (56.8%)
- **Match Threshold**: 0.9

### Visualizations

Location: `pyseqslam/results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-19-12-51-39/`

1. **oxford_difference_matrix.png**  
   Heatmap of reference vs query similarity.

2. **oxford_matchings.png**  
   Scatter plot of matched frames (ideal is a diagonal).

## Notes

- A runtime warning about a divide by zero can occur when the second-best score is zero. This does not stop the run.
- This result is suitable for cross-model comparison using the same reference/query split.

## How to Run

```bash
/Users/asadbeknematov/Desktop/Projects/slam/pySeqSLAM/.venv/bin/python /Users/asadbeknematov/Desktop/Projects/slam/pySeqSLAM/pyseqslam/run_oxford.py
```
