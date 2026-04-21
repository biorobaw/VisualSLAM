import os
import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run SLAM experiments")
    parser.add_argument("--iterations", type=int, default=5, help="Number of iterations to run for each experiment")
    args = parser.parse_args()

    # Resolve the repository root from this script's location so that all
    # relative paths work regardless of the caller's working directory.
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Dual-environment support: use ORB_SLAM3_ROOT env var (set in dev container)
    # or fall back to the local macOS build path
    orb_root_env = os.environ.get("ORB_SLAM3_ROOT")
    if orb_root_env:
        orb_root = orb_root_env
    else:
        orb_root = os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "ORB_SLAM3")
    orb_binary = os.path.join(orb_root, "Examples", "Monocular", "mono_tum")
    vocab_file = os.path.join(orb_root, "Vocabulary", "ORBvoc.txt")

    experiments = [
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_oxford.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "1)ORC-sun-2014-05-14-13-46-12", "stereo", "centre"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "1)ORC-sun-2014-05-14-13-46-12", "ORC.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "1)ORC-sun-2014-05-14-13-46-12")
        },
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_webots.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "2)city_sim", "city_sim_day_centerline", "mono_front"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "2)city_sim", "webots.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "2)city_sim", "city_sim_day_centerline")
        },
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_webots.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "2)city_sim", "city_sim_night_centerline", "mono_front"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "2)city_sim", "webots.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "2)city_sim", "city_sim_night_centerline")
        },
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_webots.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "3)village_sim", "village_sim_day_centerline_smooth", "mono_front"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "3)village_sim", "webots.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "3)village_sim", "village_sim_day_centerline_smooth")
        },
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_webots.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "3)village_sim", "village_sim_winter_centerline_smooth", "mono_front"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "3)village_sim", "webots.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "3)village_sim", "village_sim_winter_centerline_smooth")
        },
        {
            "script": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "run_oxford.py"),
            "dataset_dir": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "4)ORC-overcast-2014-06-26-08-53-56", "stereo", "centre"),
            "settings_yaml": os.path.join(BASE_DIR, "VisualSLAM", "Experiments", "4)ORC-overcast-2014-06-26-08-53-56", "ORC.yaml"),
            "output_base": os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results", "4)ORC-overcast-2014-06-26-08-53-56")
        }
    ]

    import datetime
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    for iteration in range(1, args.iterations + 1):
        print(f"\n======================================")
        print(f"       STARTING ITERATION {iteration} / {args.iterations}")
        print(f"======================================\n")

        for exp in experiments:
            output_tum = os.path.join(exp["output_base"], date_str, str(iteration), "estimation.tum")
            
            cmd = [
                sys.executable,
                exp["script"],
                "--dataset_dir", exp["dataset_dir"],
                "--orb_binary", orb_binary,
                "--vocab_file", vocab_file,
                "--settings_yaml", exp["settings_yaml"],
                "--output_tum", output_tum
            ]

            print(f"--> Running {exp['script']} on {exp['dataset_dir']} (Iteration {iteration})")
            print(f"Command: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=True)
                print(f"Successfully finished iteration {iteration} for {exp['dataset_dir']}\n")
            except subprocess.CalledProcessError as e:
                print(f"Error running iteration {iteration} for {exp['dataset_dir']}. Exited with code {e.returncode}\n")

    print("\n======================================")
    print("       COMPUTING METRICS")
    print("======================================\n")
    
    compute_cmd = [
        sys.executable,
        os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "compute_metrics.py"),
        "--results_dir", os.path.join(BASE_DIR, "VisualSLAM", "ORB_SLAM", "results")
    ]
    
    print(f"Executing: {' '.join(compute_cmd)}")
    try:
        subprocess.run(compute_cmd, check=True)
        print("Successfully generated all evaluation metrics, zips, and plots.")
    except subprocess.CalledProcessError as e:
        print(f"Error computing metrics. Exited with code {e.returncode}")

if __name__ == "__main__":
    main()
