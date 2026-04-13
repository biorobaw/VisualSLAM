# ORB-SLAM3 Evaluation Pipeline

This directory contains the Python scripts necessary to evaluate the **ORB-SLAM3** monocular SLAM system against the Oxford RobotCar and Webots datasets. It handles ground truth conversion to TUM format, wrapper executions around the ORB-SLAM3 binary, and the automated computation of Absolute Trajectory Error (ATE) and Relative Pose Error (RPE) metrics via `evo`.

## Requirements

Ensure you have installed the required Python dependencies listed in the main `VisualSLAM/requirements.txt`:
```bash
pip install "evo>=1.2.0" "scipy>=1.7.0" "pandas>=1.3.0" "matplotlib>=3.4.0"
```

Additionally, you need a compiled ORB-SLAM3 executable (e.g., `mono_tum`) and the vocabulary file (`ORBvoc.txt`).

---

## Pipeline Usage

The pipeline is split into four distinct phases.

### 1. Ground Truth Preparation

All Ground Truth (GT) and estimated trajectories use the standardized **TUM** format (`timestamp tx ty tz qx qy qz qw`).

**For Oxford RobotCar:**
Convert the Oxford `ins.csv` to TUM format:
```bash
python3 convert_oxford_to_tum.py <path_to_ins.csv> data/oxford_groundtruth.tum
```

**For Webots Simulator:**
Webots ground truths are converted from `poses.csv` to TUM format using the cross-model conversion script:
```bash
python3 ../SEQ_SLAM/reports/cross_model/scripts/convert_sim_poses_to_tum.py \
    --input ../SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/poses.csv \
    --output ../SEQ_SLAM/datasets/city_sim/city_sim_night_centerline/groundtruth.tum \
    --use-frame-id-time
```
*(Note: Webots `groundtruth.tum` files may already exist if generated previously.)*

### 2. Running ORB-SLAM3

Run ORB-SLAM3 on datasets to produce an estimated trajectory. The wrappers automatically generate the `rgb.txt` timestamp association files and pass the commands to the ORB-SLAM3 binary. 

**For Oxford Datasets:**
```bash
python3 run_oxford.py \
    --dataset_dir <path_to_oxford_images> \
    --orb_binary <path_to_mono_tum_executable> \
    --vocab_file <path_to_ORBvoc.txt> \
    --settings_yaml <path_to_camera_settings.yaml> \
    --output_tum results/oxford_sequence_mono_trajectory.tum
```

**For Webots Datasets:**
```bash
python3 run_webots.py \
    --dataset_dir <path_to_webots_scenario_folder> \
    --orb_binary <path_to_mono_tum_executable> \
    --vocab_file <path_to_ORBvoc.txt> \
    --settings_yaml <path_to_camera_settings.yaml> \
    --output_tum results/webots_scenario_trajectory.tum
```

### 3. Metric Evaluation

Calculate the Absolute Trajectory Error (ATE) and Relative Pose Error (RPE) for the generated estimations against the ground truths using `compute_metrics.py`.

```bash
python3 compute_metrics.py \
    --results_dir results \
    --gt_dir data \
    --output_csv results/metrics_summary.csv
```
This loops through all `*_trajectory.tum` files in `--results_dir`, aligns them via Umeyama alignment, runs `evo_ape` and `evo_rpe`, and compiles a final CSV matrix summary.

*(For Webots, ensure the GT trajectories are placed in the paths expected by the script or are accessible in the `datasets` folder.)*

### 4. Comparative Analysis Report

Generates a master metrics table and a PDF containing ATE and RPE comparison bar charts against other SLAM baselines (e.g., SEQ_SLAM, RAT_SLAM). It also generates trajectory top-down overlays using `evo_traj`.

```bash
python3 comparative_analysis.py \
    --orb_csv results/metrics_summary.csv \
    --gt_dir data \
    --output_dir results
```

Check the `results` folder for `comparative_report.pdf`, `master_comparison.csv`, and individual trajectory PNG overlays.