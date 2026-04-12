import argparse
import os
import subprocess
import glob
import pandas as pd
import re

def parse_evo_output(output_text):
    """
    Parse standard evo output text to extract metric statistics.
    Returns a dictionary of the parsed values.
    """
    metrics = {}
    lines = output_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Expected format: "rmse    1.234567"
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0].replace(':', '').lower()
            try:
                # Sometimes there's a unit like 'm' or 'deg' at the end, try to parse the number
                val = float(parts[1])
                if key in ['rmse', 'mean', 'median', 'min', 'max', 'std', 'sse']:
                    metrics[key] = val
            except ValueError:
                pass
    return metrics

def run_evo(gt_file, est_file, metric_type="ape", align=True):
    """
    Run evo_ape or evo_rpe and return the parsed metrics.
    """
    evo_bin = "evo_" + metric_type
    if not os.path.exists(evo_bin):
        # Fallback to system path
        evo_bin = "evo_" + metric_type
        
    cmd = [evo_bin, "tum", gt_file, est_file, "--sync"]
    
    if metric_type == "ape" and align:
        cmd.extend(["--align", "umeyama"])
        
    try:
        # Run command
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return parse_evo_output(res.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running evo_{metric_type} on {est_file}:\n{e.stderr}")
        return None

def compute_metrics(results_dir, gt_dir, output_csv):
    """
    Compute ATE and RPE for all trajectory pairs.
    """
    # Assuming est files are like: oxford_{sequence}_{modality}_trajectory.tum
    # or webots_{scenario}_trajectory.tum
    est_files = glob.glob(os.path.join(results_dir, "*_trajectory.tum"))
    
    if not est_files:
        print(f"No estimated trajectory files found in {results_dir}")
        return
        
    results = []
    
    for est_file in est_files:
        filename = os.path.basename(est_file)
        
        # Determine GT file based on naming convention
        # We need the user to match GT names, but here's a generic attempt:
        if filename.startswith("oxford_"):
            # e.g. oxford_2014-12-10-18-10-50_mono_trajectory.tum
            parts = filename.split('_')
            sequence = parts[1]
            modality = parts[2]
            # Try to find matching GT
            gt_file = os.path.join(gt_dir, f"oxford_groundtruth.tum") # fallback
            specific_gt = os.path.join(gt_dir, f"oxford_{sequence}_groundtruth.tum")
            if os.path.exists(specific_gt):
                gt_file = specific_gt
        elif filename.startswith("webots_"):
            # e.g. webots_city_sim_day_trajectory.tum
            scenario = filename.replace("webots_", "").replace("_trajectory.tum", "")
            sequence = scenario
            modality = "mono" # Webots datasets are generally mono
            # Find GT in datasets dir assuming SEQ_SLAM layout or a generic webots GT
            gt_file = os.path.join(gt_dir, f"webots_{scenario}_groundtruth.tum")
            
            # Note: For our immediate setup we might need to adjust paths if user places GT elsewhere
            # fallback to SEQ_SLAM dataset paths
            alt_gt = os.path.join("VisualSLAM/SEQ_SLAM/datasets", scenario, "groundtruth.tum")
            if not os.path.exists(gt_file) and os.path.exists(alt_gt):
                gt_file = alt_gt
        else:
            sequence = filename
            modality = "unknown"
            gt_file = os.path.join(gt_dir, filename.replace("trajectory", "groundtruth"))
            
        if not os.path.exists(gt_file):
            print(f"Warning: GT file {gt_file} not found for {est_file}. Skipping.")
            continue
            
        print(f"Evaluating {filename} against {gt_file}...")
        
        # ATE
        ate_metrics = run_evo(gt_file, est_file, "ape", align=True)
        # RPE
        rpe_metrics = run_evo(gt_file, est_file, "rpe", align=False)
        
        if ate_metrics and rpe_metrics:
            row = {
                "Sequence": sequence,
                "Modality": modality,
                "ATE_RMSE": ate_metrics.get("rmse"),
                "ATE_Mean": ate_metrics.get("mean"),
                "ATE_Median": ate_metrics.get("median"),
                "ATE_Min": ate_metrics.get("min"),
                "ATE_Max": ate_metrics.get("max"),
                "RPE_RMSE": rpe_metrics.get("rmse"),
                "RPE_Mean": rpe_metrics.get("mean"),
                "RPE_Median": rpe_metrics.get("median"),
                "RPE_Min": rpe_metrics.get("min"),
                "RPE_Max": rpe_metrics.get("max")
            }
            results.append(row)
            
    if results:
        df = pd.DataFrame(results)
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False)
        print(f"Metrics saved to {output_csv}")
    else:
        print("No metrics computed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute ATE and RPE metrics via evo.')
    parser.add_argument('--results_dir', default='VisualSLAM/ORB_SLAM/results', help='Directory with estimated trajectories')
    parser.add_argument('--gt_dir', default='VisualSLAM/ORB_SLAM/data', help='Directory with ground truth trajectories')
    parser.add_argument('--output_csv', default='VisualSLAM/ORB_SLAM/results/metrics_summary.csv', help='Path to output CSV')
    
    args = parser.parse_args()
    compute_metrics(args.results_dir, args.gt_dir, args.output_csv)
