import argparse
import os
import subprocess
import glob
import shutil
import datetime

def run_oxford(dataset_dir, orb_binary, vocab_file, settings_yaml, output_tum):
    """
    Run ORB-SLAM3 on Oxford RobotCar dataset.
    """
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory {dataset_dir} does not exist.")
        return
        
    # Build image association file if needed or just use dataset directory.
    # ORB-SLAM3's mono_euroc generally expects:
    # ./mono_euroc path_to_vocabulary path_to_settings path_to_sequence path_to_timestamps
    # We'll use mono_tum which expects:
    # ./mono_tum path_to_vocabulary path_to_settings path_to_sequence
    # For mono_tum, the dataset_dir must contain an `rgb.txt` file associating timestamps and images.
    
    # 1. Build rgb.txt
    rgb_file_path = os.path.join(dataset_dir, "rgb.txt")
    images = glob.glob(os.path.join(dataset_dir, "data", "*.png")) + glob.glob(os.path.join(dataset_dir, "*.png"))
    
    if not images:
        print(f"Warning: No PNG images found in {dataset_dir} or {dataset_dir}/data")
    else:
        # Sort images by name (which is typically the timestamp)
        images.sort()
        with open(rgb_file_path, "w") as f:
            for img in images:
                filename = os.path.basename(img)
                # Timestamp is usually the filename without extension, divide by 1e6 for seconds
                timestamp_str = os.path.splitext(filename)[0]
                try:
                    ts = float(timestamp_str) / 1e6
                    rel_path = os.path.relpath(img, dataset_dir)
                    f.write(f"{ts:.6f} {rel_path}\n")
                except ValueError:
                    pass
        print(f"Generated image association file: {rgb_file_path}")

    # 2. Call ORB-SLAM3 directly
    cmd = [
        orb_binary,
        vocab_file,
        settings_yaml,
        dataset_dir
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    import sys
    # Generate the report text
    report_file = os.path.splitext(output_tum)[0] + "_report.txt"
    os.makedirs(os.path.dirname(output_tum), exist_ok=True)
    with open(report_file, "w") as rf:
        rf.write("=== ORB-SLAM3 Oxford Run Report ===\n")
        rf.write(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        rf.write(f"Dataset Directory: {dataset_dir}\n")
        rf.write(f"Settings YAML: {settings_yaml}\n")
        rf.write(f"ORB Binary: {orb_binary}\n")
        rf.write(f"Vocab File: {vocab_file}\n")
        rf.write(f"Python Command: {' '.join(sys.argv)}\n")
        rf.write(f"Executed Command: {' '.join(cmd)}\n")
        rf.write("===================================\n")
    print(f"Generated run report: {report_file}")
    
    try:
        # We use subprocess.run, it will output CameraTrajectory.txt or KeyFrameTrajectory.txt in CWD
        subprocess.run(cmd, check=True)
        
        # 3. Rename and move output to target output_tum
        # ORB-SLAM3 typical outputs:
        generated_files = ["CameraTrajectory.txt", "KeyFrameTrajectory.txt", "f_dataset-mono.txt"]
        found = False
        for g_file in generated_files:
            if os.path.exists(g_file):
                os.makedirs(os.path.dirname(output_tum), exist_ok=True)
                shutil.move(g_file, output_tum)
                print(f"Moved {g_file} to {output_tum}")
                found = True
                break
                
        if not found:
            print("Warning: ORB-SLAM3 finished but no trajectory file was found in CWD.")
            return
            
        if os.path.getsize(output_tum) == 0:
            print(f"Warning: The generated trajectory file ({output_tum}) is empty!")
            return

        # Copy ground truth file if it exists
        experiment_root = os.path.dirname(os.path.dirname(dataset_dir))
        gt_files = glob.glob(os.path.join(experiment_root, "gps", "*_groundtruth.tum"))
        if gt_files:
            gt_file = gt_files[0]
            out_dir = os.path.dirname(output_tum)
            base_name = os.path.splitext(os.path.basename(output_tum))[0]
            
            if base_name.endswith("_estimation"):
                gt_name = base_name.replace("_estimation", "_groundtruth") + ".tum"
            elif base_name.endswith("estimation"):
                gt_name = base_name.replace("estimation", "groundtruth") + ".tum"
            else:
                gt_name = base_name + "_groundtruth.tum"
                
            local_gt = os.path.join(out_dir, gt_name)
            try:
                shutil.copy2(gt_file, local_gt)
                print(f"Copied ground truth to {local_gt}")
            except Exception as e:
                print(f"Failed to copy ground truth: {e}")
        else:
            print("Warning: No groundtruth.tum found in gps/, skipping ground truth copy.")

    except subprocess.CalledProcessError as e:
        print(f"ORB-SLAM3 execution failed: {e}")
    except FileNotFoundError:
        print(f"Could not find ORB-SLAM3 binary at {orb_binary}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run ORB-SLAM3 on Oxford Dataset')
    parser.add_argument('--dataset_dir', required=True, help='Path to Oxford image directory')
    parser.add_argument('--orb_binary', default='./src/ORB_SLAM3/Examples/Monocular/mono_tum', help='Path to ORB-SLAM3 executable')
    parser.add_argument('--vocab_file', default='./src/ORB_SLAM3/Vocabulary/ORBvoc.txt', help='Path to ORBvoc.txt')
    parser.add_argument('--settings_yaml', default='../../Experiments/2014-05-14-13-46-12/test.yaml', help='Path to camera settings YAML')
    parser.add_argument('--output_tum', required=True, help='Path to save output TUM trajectory')
    
    args = parser.parse_args()
    run_oxford(args.dataset_dir, args.orb_binary, args.vocab_file, args.settings_yaml, args.output_tum)
