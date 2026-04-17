import argparse
import os
import subprocess
import glob
import shutil
import datetime
import sys

def run_webots(dataset_dir, orb_binary, vocab_file, settings_yaml, output_tum):
    """
    Run ORB-SLAM3 on Webots simulator dataset, generate a report, and save an evo zip file.
    """
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory {dataset_dir} does not exist.")
        return
        
    # Find image directory, usually mono_front or directly in dataset_dir
    img_dir = os.path.join(dataset_dir, "mono_front")
    if not os.path.exists(img_dir):
        img_dir = dataset_dir
        
    # Build rgb.txt
    rgb_file_path = os.path.join(dataset_dir, "rgb.txt")
    images = glob.glob(os.path.join(img_dir, "*.png"))
    
    if not images:
        print(f"Warning: No PNG images found in {img_dir}")
    else:
        # Sort images by name
        images.sort()
        with open(rgb_file_path, "w") as f:
            for img in images:
                filename = os.path.basename(img)
                # The filename is something like 0001.png
                frame_str = os.path.splitext(filename)[0]
                try:
                    ts = float(int(frame_str))  # Using frame_id directly as timestamp
                    rel_path = os.path.relpath(img, dataset_dir)
                    f.write(f"{ts:.6f} {rel_path}\n")
                except ValueError:
                    pass
        print(f"Generated image association file: {rgb_file_path}")

    # Call ORB-SLAM3 directly
    cmd = [
        orb_binary,
        vocab_file,
        settings_yaml,
        dataset_dir
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Generate the report text
    report_file = os.path.splitext(output_tum)[0] + "_report.txt"
    os.makedirs(os.path.dirname(output_tum), exist_ok=True)
    with open(report_file, "w") as rf:
        rf.write("=== ORB-SLAM3 Webots Run Report ===\n")
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
        subprocess.run(cmd, check=True)
        
        generated_files = ["CameraTrajectory.txt", "KeyFrameTrajectory.txt", "f_dataset-mono.txt"]
        found = False
        for g_file in generated_files:
            if os.path.exists(g_file):
                shutil.move(g_file, output_tum)
                print(f"Moved {g_file} to {output_tum}")
                found = True
                break
                
        if not found:
            print("Warning: ORB-SLAM3 finished but no trajectory file was found in CWD.")
            return

        # Attempt to run evo_ape if groundtruth exists
        gt_file = os.path.join(dataset_dir, "groundtruth.tum")
        if os.path.exists(gt_file):
            # Check if output is empty
            if os.path.getsize(output_tum) == 0:
                print(f"Warning: The generated trajectory file ({output_tum}) is empty!")
                print("This means ORB-SLAM3 failed to track any keyframes. Are you using the correct camera settings YAML for this dataset?")
                return
                
            zip_output = os.path.splitext(output_tum)[0] + "_evo.zip"
            # Use --align and --correct_scale for full Sim3 Umeyama alignment
            evo_cmd = ["evo_ape", "tum", gt_file, output_tum, "--align", "--correct_scale", "--save_results", zip_output]
            print(f"Executing evo: {' '.join(evo_cmd)}")
            try:
                subprocess.run(evo_cmd, check=True)
                print(f"Successfully generated evo zip file: {zip_output}")
            except subprocess.CalledProcessError as e:
                print(f"Evo execution failed: {e}")
            except FileNotFoundError:
                print("Evo executable not found. Make sure you have installed evo (e.g. pip install evo).")
        else:
            print(f"Warning: No groundtruth.tum found in {dataset_dir}, skipping evo_ape.")
            
    except subprocess.CalledProcessError as e:
        print(f"ORB-SLAM3 execution failed: {e}")
    except FileNotFoundError:
        print(f"Could not find ORB-SLAM3 binary at {orb_binary}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run ORB-SLAM3 on Webots Dataset')
    parser.add_argument('--dataset_dir', required=True, help='Path to Webots dataset directory (e.g. city_sim_night_centerline)')
    parser.add_argument('--orb_binary', default='./src/ORB_SLAM3/Examples/Monocular/mono_tum', help='Path to ORB-SLAM3 executable')
    parser.add_argument('--vocab_file', default='./src/ORB_SLAM3/Vocabulary/ORBvoc.txt', help='Path to ORBvoc.txt')
    parser.add_argument('--settings_yaml', required=True, help='Path to camera settings YAML')
    parser.add_argument('--output_tum', required=True, help='Path to save output TUM trajectory')
    
    args = parser.parse_args()
    run_webots(args.dataset_dir, args.orb_binary, args.vocab_file, args.settings_yaml, args.output_tum)