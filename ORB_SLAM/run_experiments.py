import os
import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run SLAM experiments")
    parser.add_argument("--iterations", type=int, default=5, help="Number of iterations to run for each experiment")
    args = parser.parse_args()

    orb_binary = "VisualSLAM/ORB_SLAM/ORB_SLAM3/Examples/Monocular/mono_tum"
    vocab_file = "VisualSLAM/ORB_SLAM/ORB_SLAM3/Vocabulary/ORBvoc.txt"

    experiments = [
        {
            "script": "VisualSLAM/ORB_SLAM/run_oxford.py",
            "dataset_dir": "VisualSLAM/Experiments/1)ORC-sun-2014-05-14-13-46-12/stereo/centre",
            "settings_yaml": "VisualSLAM/Experiments/1)ORC-sun-2014-05-14-13-46-12/ORC.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/1)ORC-sun-2014-05-14-13-46-12"
        },
        {
            "script": "VisualSLAM/ORB_SLAM/run_webots.py",
            "dataset_dir": "VisualSLAM/Experiments/2)city_sim/city_sim_day_centerline/mono_front",
            "settings_yaml": "VisualSLAM/Experiments/2)city_sim/webots.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/2)city_sim/city_sim_day_centerline"
        },
        {
            "script": "VisualSLAM/ORB_SLAM/run_webots.py",
            "dataset_dir": "VisualSLAM/Experiments/2)city_sim/city_sim_night_centerline/mono_front",
            "settings_yaml": "VisualSLAM/Experiments/2)city_sim/webots.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/2)city_sim/city_sim_night_centerline"
        },
        {
            "script": "VisualSLAM/ORB_SLAM/run_webots.py",
            "dataset_dir": "VisualSLAM/Experiments/3)village_sim/village_sim_day_centerline_smooth/mono_front",
            "settings_yaml": "VisualSLAM/Experiments/3)village_sim/webots.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/3)village_sim/village_sim_day_centerline_smooth"
        },
        {
            "script": "VisualSLAM/ORB_SLAM/run_webots.py",
            "dataset_dir": "VisualSLAM/Experiments/3)village_sim/village_sim_winter_centerline_smooth/mono_front",
            "settings_yaml": "VisualSLAM/Experiments/3)village_sim/webots.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/3)village_sim/village_sim_winter_centerline_smooth"
        },
        {
            "script": "VisualSLAM/ORB_SLAM/run_oxford.py",
            "dataset_dir": "VisualSLAM/Experiments/4)ORC-overcast-2014-06-26-08-53-56/stereo/centre",
            "settings_yaml": "VisualSLAM/Experiments/4)ORC-overcast-2014-06-26-08-53-56/ORC.yaml",
            "output_base": "VisualSLAM/ORB_SLAM/results/4)ORC-overcast-2014-06-26-08-53-56"
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
        "VisualSLAM/ORB_SLAM/compute_metrics.py",
        "--results_dir", "VisualSLAM/ORB_SLAM/results"
    ]
    
    print(f"Executing: {' '.join(compute_cmd)}")
    try:
        subprocess.run(compute_cmd, check=True)
        print("Successfully generated all evaluation metrics, zips, and plots.")
    except subprocess.CalledProcessError as e:
        print(f"Error computing metrics. Exited with code {e.returncode}")

if __name__ == "__main__":
    main()
