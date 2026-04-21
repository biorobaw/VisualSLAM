import argparse
import os
import subprocess
import glob
import pandas as pd

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

def run_evo_command(cmd, est_file, metric_name):
    """
    Run a specific evo command and return the parsed metrics.
    """
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return parse_evo_output(res.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {metric_name} on {est_file}:\n{e.stderr}")
        return None

def compute_metrics(results_dir, output_csv):
    """
    Compute ATE and RPE for all trajectory pairs.
    """
    # Assuming est files are like: oxford_{sequence}_{modality}_estimation.tum
    # or webots_{scenario}_estimation.tum, or inside nested experiment directories.
    est_files = glob.glob(os.path.join(results_dir, "**", "*estimation.tum"), recursive=True)
    
    if not est_files:
        print(f"No estimated trajectory files found in {results_dir}")
        return
        
    results = []
    
    for est_file in est_files:
        filename = os.path.basename(est_file)
        
        out_dir = os.path.dirname(est_file)
        base_name = os.path.splitext(filename)[0]
        
        # Try to extract sequence from the directory path if it's a generic "estimation.tum"
        parts = est_file.split(os.sep)
        if len(parts) >= 4 and parts[-1] == "estimation.tum":
            sequence = parts[-4]
        else:
            sequence = base_name.replace("_estimation", "").replace("estimation", "run")
        modality = "mono"
            
        if base_name.endswith("_estimation"):
            gt_name = base_name.replace("_estimation", "_groundtruth") + ".tum"
        elif base_name.endswith("estimation"):
            gt_name = base_name.replace("estimation", "groundtruth") + ".tum"
        else:
            gt_name = base_name + "_groundtruth.tum"
            
        gt_file = os.path.join(out_dir, gt_name)
            
        if not os.path.exists(gt_file):
            print(f"Warning: GT file {gt_file} not found for {est_file}. Skipping.")
            continue
            
        print(f"Evaluating {filename} against {gt_file}...")
        
        ape_trans_zip = os.path.join(out_dir, f"{base_name}_ape_trans_results.zip")
        ape_trans_plot = os.path.join(out_dir, f"{base_name}_ape_trans_plot.png")
        rpe_trans_zip = os.path.join(out_dir, f"{base_name}_rpe_trans_results.zip")
        rpe_trans_plot = os.path.join(out_dir, f"{base_name}_rpe_trans_plot.png")
        rpe_rot_zip = os.path.join(out_dir, f"{base_name}_rpe_rot_results.zip")
        rpe_rot_plot = os.path.join(out_dir, f"{base_name}_rpe_rot_plot.png")
        traj_plot = os.path.join(out_dir, f"{base_name}_traj_xy_plot.png")
        
        # Define evo commands
        common_flags = ["-as", "--project_to_plane", "xy", "--no_warnings"]
        cmd_ape_trans = ["evo_ape", "tum", gt_file, est_file] + common_flags + ["-r", "trans_part", "--save_results", ape_trans_zip, "--save_plot", ape_trans_plot]
        cmd_rpe_trans = ["evo_rpe", "tum", gt_file, est_file] + common_flags + ["-r", "trans_part", "--save_results", rpe_trans_zip, "--save_plot", rpe_trans_plot]
        cmd_rpe_rot = ["evo_rpe", "tum", gt_file, est_file] + common_flags + ["-r", "angle_deg", "--save_results", rpe_rot_zip, "--save_plot", rpe_rot_plot]
        cmd_traj = ["evo_traj", "tum", gt_file, est_file] + common_flags + ["--plot_mode xy", "--save_plot", traj_plot]
                
        # ATE Translation
        ate_trans_metrics = run_evo_command(cmd_ape_trans, est_file, "APE Translation")
        # RPE Translation
        rpe_trans_metrics = run_evo_command(cmd_rpe_trans, est_file, "RPE Translation")
        # RPE Rotation
        rpe_rot_metrics = run_evo_command(cmd_rpe_rot, est_file, "RPE Rotation")
        

        try:
            subprocess.run(cmd_traj, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            print(f"  Saved trajectory plot: {traj_plot}")
        except subprocess.CalledProcessError as e:
            print(f"  Warning: evo_traj plot failed for {est_file}:\n{e.stderr}")

        if ate_trans_metrics and rpe_trans_metrics and rpe_rot_metrics:
            row = {
                "Sequence": sequence,
                "Modality": modality,
                "ATE_Trans_RMSE": ate_trans_metrics.get("rmse"),
                "ATE_Trans_Mean": ate_trans_metrics.get("mean"),
                "ATE_Trans_Median": ate_trans_metrics.get("median"),
                "ATE_Trans_Min": ate_trans_metrics.get("min"),
                "ATE_Trans_Max": ate_trans_metrics.get("max"),
                "RPE_Trans_RMSE": rpe_trans_metrics.get("rmse"),
                "RPE_Trans_Mean": rpe_trans_metrics.get("mean"),
                "RPE_Trans_Median": rpe_trans_metrics.get("median"),
                "RPE_Trans_Min": rpe_trans_metrics.get("min"),
                "RPE_Trans_Max": rpe_trans_metrics.get("max"),
                "RPE_Rot_RMSE": rpe_rot_metrics.get("rmse"),
                "RPE_Rot_Mean": rpe_rot_metrics.get("mean"),
                "RPE_Rot_Median": rpe_rot_metrics.get("median"),
                "RPE_Rot_Min": rpe_rot_metrics.get("min"),
                "RPE_Rot_Max": rpe_rot_metrics.get("max")
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
    parser.add_argument('--gt_dir', default='VisualSLAM/ORB_SLAM/results', help='Directory with ground truth trajectories')
    parser.add_argument('--output_csv', default='VisualSLAM/ORB_SLAM/results/metrics_summary.csv', help='Path to output CSV')
    
    args = parser.parse_args()
    compute_metrics(args.results_dir, args.gt_dir, args.output_csv)
