"""
Script to run SeqSLAM experiments with different sequence lengths
and save the results automatically without showing plots.
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid hanging on plt.show()

from parameters import defaultParameters
from utils import AttributeDict
import matplotlib.pyplot as plt
from copy import deepcopy
import time
import os
from seqslam import *


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

def run_experiment(sequence_length):
    """Run SeqSLAM with a specific sequence length parameter"""
    
    print(f"\n{'='*60}")
    print(f"Running experiment with sequence length (ds) = {sequence_length}")
    print(f"{'='*60}\n")
    
    # Set up parameters
    params = defaultParameters()    
    
    # Nordland spring dataset
    ds = AttributeDict()
    ds.name = 'spring'
    ds.imagePath = '../datasets/nordland/64x32-grayscale-1fps/spring'
    ds.prefix='images-'
    ds.extension='.png'
    ds.suffix=''
    ds.imageSkip = 100
    ds.imageIndices = range(1, 35700, ds.imageSkip)    
    ds.savePath = 'results'
    ds.saveFile = '%s-%d-%d-%d' % (ds.name, ds.imageIndices[0], ds.imageSkip, ds.imageIndices[-1])
    ds.preprocessing = AttributeDict()
    ds.preprocessing.save = 1
    ds.preprocessing.load = 1  # Load preprocessed data to save time
    ds.crop=[]
    spring=ds

    # Nordland winter dataset
    ds2 = deepcopy(ds)
    ds2.name = 'winter'
    ds2.imagePath = '../datasets/nordland/64x32-grayscale-1fps/winter'
    ds2.saveFile = '%s-%d-%d-%d' % (ds2.name, ds2.imageIndices[0], ds2.imageSkip, ds2.imageIndices[-1])
    ds2.crop=[]
    winter=ds2      

    params.dataset = [spring, winter]
    
    # Load preprocessed results to save time
    params.differenceMatrix.load = 1
    params.contrastEnhanced.load = 1
    params.matching.load = 0
    
    params.savePath='results'
    
    # Set sequence length parameter
    params.matching.ds = sequence_length
    
    # Run SeqSLAM
    ss = SeqSLAM(params)  
    t1 = time.time()
    results = ss.run()
    t2 = time.time()          
    print(f"Time taken: {t2-t1:.2f} seconds")
    
    # Plot 1: Difference Matrix (heatmap)
    if hasattr(results, 'DD') and results.DD is not None:
        plt.figure(figsize=(10, 8))
        plt.imshow(results.DD, aspect='auto', cmap='hot', interpolation='nearest')
        plt.colorbar(label='Difference (lower=more similar)')
        plt.xlabel('Winter sequence frame')
        plt.ylabel('Spring sequence frame')
        plt.title(f'SeqSLAM Contrast-Enhanced Difference Matrix (ds={sequence_length})')
        filename = f'results/nordland/difference_matrix_ds{sequence_length}.png'
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
        plt.xlabel('Winter sequence frame')
        plt.ylabel('Matched spring sequence frame')
        plt.ylim(bottom=invalid_y * 1.5)
        plt.title(
            f'Matchings '
            f'(ds={sequence_length}, thresh={thresh}, '
            f'valid={valid_matches}, invalid={invalid_matches})'
        )
        plt.legend()
        filename = f'results/nordland/matchings_ds{sequence_length}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filename}")
        
        print(f"\n{'='*60}")
        print(f"Experiment completed!")
        print(f"Valid matches: {valid_matches}/{len(m)} ({100*valid_matches/len(m):.1f}%)")
        print(f"Invalid matches: {invalid_matches}/{len(m)} ({100*invalid_matches/len(m):.1f}%)")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    # Create results directory if it doesn't exist
    os.makedirs('results/nordland', exist_ok=True)
    
    # Run experiments with different sequence lengths
    sequence_lengths = [10, 20, 30]
    
    for ds in sequence_lengths:
        run_experiment(ds)
    
    print("\n" + "="*60)
    print("All experiments completed!")
    print("Results saved in: results/nordland/")
    print("="*60)
