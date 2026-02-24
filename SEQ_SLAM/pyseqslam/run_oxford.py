"""
Script to run SeqSLAM on Oxford RobotCar dataset.
Uses two different runs (reference/query) to simulate revisiting.
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from parameters import defaultParameters
from utils import AttributeDict
import matplotlib.pyplot as plt
from copy import deepcopy
import time
import os
from seqslam import *
import glob


def _split_match_indices(matches, thresh=0.9, min_match_index=1):
    """Return valid/invalid masks for match indices used in plotting."""
    match_idx = np.asarray(matches[:, 0], dtype=float).copy()
    quality = np.asarray(matches[:, 1], dtype=float)

    finite = np.isfinite(match_idx) & np.isfinite(quality)
    strong_enough = quality <= thresh
    plausible_index = match_idx >= min_match_index

    valid_mask = finite & strong_enough & plausible_index
    invalid_mask = ~valid_mask
    return match_idx, valid_mask, invalid_mask

def _load_timestamps(image_path):
    all_images = sorted(glob.glob(f"{image_path}/*.png"))
    timestamps = [int(os.path.basename(img).replace('.png', '')) for img in all_images]
    return all_images, timestamps


def run_oxford_experiment():
    """Run SeqSLAM on Oxford RobotCar dataset"""
    
    print(f"\n{'='*60}")
    print(f"Running SeqSLAM on Oxford RobotCar Dataset")
    print(f"{'='*60}\n")
    
    # Set up parameters
    params = defaultParameters()
    
    # Enable resizing for Oxford images (1024x1024 -> 32x64)
    params.DO_RESIZE = 1
    
    # Oxford dataset - reference/query runs (alt route)
    reference_path = '../datasets/oxford/2014-05-14-13-46-12/mono_left'
    query_path = '../datasets/oxford/2014-05-19-12-51-39/mono_left'

    ref_images, ref_timestamps = _load_timestamps(reference_path)
    qry_images, qry_timestamps = _load_timestamps(query_path)

    print(f"Reference images found: {len(ref_images)}")
    print(f"Query images found: {len(qry_images)}")
    print(f"Reference indices: {ref_timestamps[0]} to {ref_timestamps[-1]}")
    print(f"Query indices: {qry_timestamps[0]} to {qry_timestamps[-1]}")
    
    # First sequence dataset
    ds1 = AttributeDict()
    ds1.name = 'oxford_reference'
    ds1.imagePath = reference_path
    ds1.prefix = ''
    ds1.extension = '.png'
    ds1.suffix = ''
    ds1.imageSkip = 1  # Use all images (or increase to skip frames)
    ds1.imageIndices = ref_timestamps
    ds1.savePath = 'results'
    ds1.saveFile = 'oxford_reference'  # Simplified filename
    ds1.preprocessing = AttributeDict()
    ds1.preprocessing.save = 1
    ds1.preprocessing.load = 0  # First run, don't try to load
    ds1.crop = []
    
    # Second sequence dataset
    ds2 = deepcopy(ds1)
    ds2.name = 'oxford_query'
    ds2.imagePath = query_path
    ds2.imageIndices = qry_timestamps
    ds2.saveFile = 'oxford_query'  # Simplified filename
    
    params.dataset = [ds1, ds2]
    
    # Don't try to load preprocessed results on first run
    params.differenceMatrix.load = 0
    params.contrastEnhanced.load = 0
    params.matching.load = 0
    
    params.savePath = 'results'
    
    # Set sequence length parameter
    params.matching.ds = 10  # Start with default
    
    # Run SeqSLAM
    ss = SeqSLAM(params)  
    t1 = time.time()
    results = ss.run()
    t2 = time.time()          
    print(f"\nTime taken: {t2-t1:.2f} seconds")
    
    # Plot 1: Difference Matrix (heatmap)
    if hasattr(results, 'DD') and results.DD is not None:
        plt.figure(figsize=(10, 8))
        plt.imshow(results.DD, aspect='auto', cmap='hot', interpolation='nearest')
        plt.colorbar(label='Difference (lower=more similar)')
        plt.xlabel('Second sequence frame')
        plt.ylabel('First sequence frame')
        plt.title(f'SeqSLAM Difference Matrix - Oxford RobotCar')
        filename = f'results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-19-12-51-39/oxford_difference_matrix.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
    
    # Plot 2: Matching results (scatter plot)
    if len(results.matches) > 0:
        plt.figure(figsize=(10, 6))
        thresh = 0.9
        m, valid_mask, invalid_mask = _split_match_indices(results.matches, thresh=thresh)
        x = np.arange(len(m))
        
        # Count valid matches
        valid_matches = int(np.sum(valid_mask))
        invalid_matches = int(np.sum(invalid_mask))

        if valid_matches > 0:
            plt.scatter(x[valid_mask], m[valid_mask], s=10, label='Valid matches')

        invalid_y = -0.03 * len(m)
        if invalid_matches > 0:
            plt.scatter(
                x[invalid_mask],
                np.full(invalid_matches, invalid_y),
                s=12,
                marker='x',
                color='tab:red',
                label='Invalid/filtered matches',
            )

        # Add diagonal reference line
        plt.plot([0, len(m)], [0, len(m)], 'r--', alpha=0.3, label='Perfect diagonal')
        plt.xlabel('Second sequence frame')
        plt.ylabel('Matched first sequence frame')
        plt.ylim(bottom=invalid_y * 1.5)
        plt.title(
            f'Matchings - Oxford RobotCar '
            f'(ds={params.matching.ds}, valid={valid_matches}, invalid={invalid_matches})'
        )
        plt.legend()
        filename = f'results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-19-12-51-39/oxford_matchings.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
        
    print(f"\n{'='*60}")
    print(f"Oxford RobotCar experiment completed!")
    print(f"Valid matches: {valid_matches}/{len(m)} ({100*valid_matches/len(m):.1f}%)")
    print(f"Invalid matches: {invalid_matches}/{len(m)} ({100*invalid_matches/len(m):.1f}%)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs('results/oxford/Oxford_2014-05-14-13-46-12_vs_2014-05-19-12-51-39', exist_ok=True)
    
    run_oxford_experiment()
