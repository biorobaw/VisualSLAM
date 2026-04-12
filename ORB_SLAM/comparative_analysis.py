import argparse
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import subprocess

def run_evo_plot(gt_file, est_files, output_png):
    """
    Generate trajectory overlay plot using evo_traj.
    est_files is a dictionary mapping method_name -> trajectory_file.
    """
    evo_bin = "evo_traj" # Let the venv find it natively
    if not os.path.exists(evo_bin):
        evo_bin = "evo_traj"
        
    cmd = [evo_bin, "tum", gt_file]
    for method, file_path in est_files.items():
        if os.path.exists(file_path):
            cmd.append(file_path)
            
    cmd.extend(["--ref", gt_file, "-p", "--plot_mode=xy", "--save_plot", output_png])
    
    print(f"Generating plot: {output_png}")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating plot {output_png}: {e.stderr}")

def generate_comparative_analysis(orb_metrics_csv, seq_slam_dir, rat_slam_dir, gt_dir, output_dir):
    """
    Generate Comparative Analysis Report
    """
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "comparative_report.pdf")
    
    # 1. Load ORB-SLAM3 results
    if os.path.exists(orb_metrics_csv):
        df_orb = pd.read_csv(orb_metrics_csv)
        df_orb['Method'] = 'ORB_SLAM3'
    else:
        print(f"Warning: ORB-SLAM3 metrics not found at {orb_metrics_csv}")
        df_orb = pd.DataFrame()
        
    # NOTE: In a full pipeline, we would load SEQ_SLAM and RAT_SLAM metrics here.
    # For MVP, we will mock or load if they exist.
    # We'll build a master DataFrame of whatever we have.
    master_df = pd.DataFrame()
    if not df_orb.empty:
        master_df = pd.concat([master_df, df_orb], ignore_axis=True)
        
    if master_df.empty:
        print("No metrics data available to generate report.")
        return
        
    # Build comparison table
    # Pivot so Rows = Sequence, Modality and Columns = Method_ATE_RMSE, etc.
    pivot_df = master_df.pivot_table(
        index=['Sequence', 'Modality'], 
        columns='Method', 
        values=['ATE_RMSE', 'RPE_RMSE']
    )
    
    # Flatten multi-index columns
    pivot_df.columns = [f"{method}_{metric}" for metric, method in pivot_df.columns]
    pivot_df.reset_index(inplace=True)
    
    csv_out = os.path.join(output_dir, "master_comparison.csv")
    pivot_df.to_csv(csv_out, index=False)
    print(f"Master comparison saved to {csv_out}")
    
    # 2. Generate Visualizations
    with PdfPages(pdf_path) as pdf:
        # ATE Bar Chart
        if 'ORB_SLAM3_ATE_RMSE' in pivot_df.columns:
            plt.figure(figsize=(10, 6))
            x = range(len(pivot_df))
            plt.bar(x, pivot_df['ORB_SLAM3_ATE_RMSE'], width=0.4, label='ORB-SLAM3')
            plt.xticks(x, pivot_df['Sequence'], rotation=45, ha='right')
            plt.ylabel('ATE RMSE (m)')
            plt.title('Absolute Trajectory Error (ATE) Comparison')
            plt.legend()
            plt.tight_layout()
            
            plt.savefig(os.path.join(output_dir, "ate_comparison.png"))
            pdf.savefig()
            plt.close()
            
        # RPE Bar Chart
        if 'ORB_SLAM3_RPE_RMSE' in pivot_df.columns:
            plt.figure(figsize=(10, 6))
            x = range(len(pivot_df))
            plt.bar(x, pivot_df['ORB_SLAM3_RPE_RMSE'], width=0.4, label='ORB-SLAM3')
            plt.xticks(x, pivot_df['Sequence'], rotation=45, ha='right')
            plt.ylabel('RPE RMSE')
            plt.title('Relative Pose Error (RPE) Comparison')
            plt.legend()
            plt.tight_layout()
            
            plt.savefig(os.path.join(output_dir, "rpe_comparison.png"))
            pdf.savefig()
            plt.close()
            
    print(f"Comparative report PDF saved to {pdf_path}")
    
    # 3. Trajectory Overlays
    # Attempt to find common sequences to plot
    # We will search for ORB-SLAM3 trajectory files, and then look for GT and others
    orb_traj_files = glob.glob(os.path.join(os.path.dirname(orb_metrics_csv), "*_trajectory.tum"))
    
    for orb_file in orb_traj_files:
        filename = os.path.basename(orb_file)
        seq_name = filename.replace("_trajectory.tum", "")
        
        # Determine GT
        if filename.startswith("webots_"):
            scenario = filename.replace("webots_", "").replace("_trajectory.tum", "")
            gt_file = os.path.join(gt_dir, f"webots_{scenario}_groundtruth.tum")
            alt_gt = os.path.join("VisualSLAM/SEQ_SLAM/datasets", scenario, "groundtruth.tum")
            if not os.path.exists(gt_file) and os.path.exists(alt_gt):
                gt_file = alt_gt
        else:
            gt_file = os.path.join(gt_dir, filename.replace("trajectory", "groundtruth"))
            
        if os.path.exists(gt_file):
            plot_png = os.path.join(output_dir, f"{seq_name}_trajectory_overlay.png")
            # In MVP, we just plot ORB vs GT. Future integration adds SEQ and RAT files here.
            est_files = {"ORB_SLAM3": orb_file}
            run_evo_plot(gt_file, est_files, plot_png)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Comparative Analysis Report.')
    parser.add_argument('--orb_csv', default='VisualSLAM/ORB_SLAM/results/metrics_summary.csv', help='Path to ORB-SLAM3 metrics CSV')
    parser.add_argument('--seq_dir', default='VisualSLAM/SEQ_SLAM/results', help='Path to SEQ_SLAM results')
    parser.add_argument('--rat_dir', default='VisualSLAM/RAT_SLAM/results', help='Path to RAT_SLAM results')
    parser.add_argument('--gt_dir', default='VisualSLAM/ORB_SLAM/data', help='Path to GT dir')
    parser.add_argument('--output_dir', default='VisualSLAM/ORB_SLAM/results', help='Output directory for report')
    
    args = parser.parse_args()
    generate_comparative_analysis(args.orb_csv, args.seq_dir, args.rat_dir, args.gt_dir, args.output_dir)
