# SeqSLAM Experiments: Oxford RobotCar Dataset

## Dataset Information

**Name**: Oxford RobotCar Dataset  
**Specific Run**: `Oxford_2014-05-14-13-50-20`  
**Date/Time**: May 14, 2014, 13:50:20  
**Camera**: Grasshopper 2 – Left (mono_left)  
**Type**: Urban driving dataset  
**Location**: Oxford, UK (city center)  
**Total Frames**: 284 images  
**Original Resolution**: 1024×1024 pixels (grayscale)  
**Processed Resolution**: 64×32 pixels (downsampled for SeqSLAM)

## Dataset Split Strategy

Since we have a single continuous sequence, we split it to simulate revisiting:

- **Sequence 1** (First Half): Frames 1-142  
  - Timestamps: `1400075430019436` to `1400075442835861`
  
- **Sequence 2** (Second Half): Frames 143-284  
  - Timestamps: `1400075442926724` to `1400075455743153`

This simulates the robot traversing the same route at different times.

## Experiment Configuration

### Key Differences from Nordland

1. **Image Format**: Already grayscale (mono camera)
2. **Resizing Required**: 1024×1024 → 64×32 (enabled `DO_RESIZE`)
3. **No Frame Skipping**: Used all 284 frames (`imageSkip = 1`)
4. **Urban Environment**: Structured features (buildings, roads) vs scenic landscape

### Parameters Used

```python
params.DO_RESIZE = 1                # Enable downsample (Oxford images are large)
params.DO_GRAYLEVEL = 1            # Grayscale conversion (handles already-gray images)
params.DO_PATCHNORMALIZATION = 1   # 8×8 patch normalization
params.matching.ds = 10            # Sequence length (default)
params.matching.vmin = 0.8         # Minimum velocity constraint
params.matching.vmax = 1.2         # Maximum velocity constraint
params.matching.Rwindow = 10       # Search window radius
params.contrastEnhancement.R = 10  # Contrast enhancement window
```

## Results

### Performance Metrics

- **Processing Time**: 3.66 seconds
- **Valid Matches**: 55/142 (38.7%)
- **Match Threshold**: 0.9 (higher = stricter)

### Visualizations Generated

**Location**: `pyseqslam/results/oxford/Oxford_2014-05-14-13-50-20/`

1. **oxford_difference_matrix.png**  
   Heatmap showing similarity between first and second half sequences.
   - X-axis: Second sequence frames (143-284)
   - Y-axis: First sequence frames (1-142)
   - Darker regions = better matches (lower difference)

2. **oxford_matchings.png**  
   Scatter plot showing matched frame pairs.
   - X-axis: Second sequence frame index
   - Y-axis: Matched first sequence frame
   - Red dashed line: Perfect diagonal (ideal matching)
   - Valid matches shown as blue dots

## Key Findings

### Urban vs Scenic Environment

**Oxford (Urban)**:
- Match rate: 38.7% (55/142 frames)
- More challenging due to repetitive structures
- Buildings and roads can look similar from different viewpoints

**Nordland (Scenic)**:
- Expected higher match rate
- More distinctive natural features
- Better performance with seasonal changes

## Code Modifications

### 1. Grayscale Handling
Modified `seqslam.py` to handle already-grayscale images:

```python
@staticmethod
def rgb2gray(rgb):
    # If already grayscale (2D array), return as is
    if len(rgb.shape) == 2:
        return rgb
    # Otherwise convert RGB to grayscale
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray
```

### 2. Image Resizing
Fixed resize function to handle numpy arrays:

```python
# Convert to PIL Image for resizing
img = Image.fromarray(img.astype('uint8'))

# PIL resize expects (width, height), params has [height, width]
img = img.resize((params.downsample.size[1], params.downsample.size[0]), 
                 params.downsample.method)
```

## Technical Details

### Image Processing Pipeline

1. **Load**: Read 1024×1024 grayscale PNG images
2. **Grayscale Check**: Detect already-gray images (skip conversion)
3. **Resize**: Downsample to 64×32 using Lanczos interpolation
4. **Patch Normalize**: Apply 8×8 patch normalization
5. **Difference Matrix**: Compute 142×142 pairwise differences
6. **Contrast Enhancement**: Local enhancement (R=10)
7. **Sequence Matching**: Find matches with ds=10, threshold=0.9

## Code Files

- **Main Script**: `pyseqslam/run_oxford.py`
- **Core Algorithm**: `pyseqslam/seqslam.py` (modified)
- **Parameters**: `pyseqslam/parameters.py`

## How to Run

```bash
cd pyseqslam
python run_oxford.py
```

## Next Steps

### Immediate
- ⬜ Tune sequence length (`ds`) for urban environment (try 15, 20, 30)
- ⬜ Test different velocity constraints (urban may need adjustment)
- ⬜ Analyze failure cases (which frames failed to match?)

### Future Experiments
- ⬜ Test on multiple Oxford runs (different times/weather)
- ⬜ Compare day vs night performance
- ⬜ Try different camera positions (left vs right vs rear)
- ⬜ Evaluate with ground truth trajectory data
- ⬜ Generate precision-recall curves

## References

- **Dataset**: [Oxford RobotCar Dataset](https://robotcar-dataset.robots.ox.ac.uk/)
- **Paper**: Maddern, W., et al. (2017). "1 Year, 1000km: The Oxford RobotCar Dataset." *IJRR*.
- **SeqSLAM Paper**: Milford, M. J., & Wyeth, G. F. (2012). "SeqSLAM: Visual route-based navigation."
