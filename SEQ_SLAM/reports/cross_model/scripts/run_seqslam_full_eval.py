#!/usr/bin/env python3
"""Run the agreed SeqSLAM sim-world/Oxford evaluation workflow end-to-end."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CROSS_MODEL_DIR = SCRIPT_DIR.parent
SEQ_SLAM_DIR = CROSS_MODEL_DIR.parent.parent
PYSEQSLAM_DIR = SEQ_SLAM_DIR / "pyseqslam"
REPO_ROOT = SEQ_SLAM_DIR.parent

SIM_WORLD_PAIRS = [
    {"dataset_group": "city", "reference_run": "city_summer", "query_run": "city_summer"},
    {"dataset_group": "city", "reference_run": "city_summer", "query_run": "city_night"},
    {"dataset_group": "village", "reference_run": "village_summer", "query_run": "village_summer"},
    {"dataset_group": "village", "reference_run": "village_summer", "query_run": "village_winter"},
]

OXFORD_PAIRS = [
    {"reference_run": "2014-05-14-13-46-12", "query_run": "2014-05-14-13-46-12"},
    {"reference_run": "2014-05-14-13-46-12", "query_run": "2014-06-23-15-36-04"},
    {"reference_run": "2014-05-14-13-46-12", "query_run": "2014-06-26-08-53-56"},
]


@dataclass
class OxfordArtifact:
    pair_id: str
    reference_run: str
    query_run: str
    image_subdir: str
    rank_score: float
    valid_ratio: float
    corr: float
    norm_mae: float
    best_ds: int
    best_vmin: float
    best_vmax: float
    best_rwindow: int
    best_threshold: float
    source_result_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full SeqSLAM sim-world + Oxford evaluation bundle")
    parser.add_argument(
        "--run-label",
        default=date.today().isoformat(),
        help="Identifier appended to result directories and bundle paths.",
    )
    parser.add_argument(
        "--python-bin",
        default=str(REPO_ROOT / ".venv" / "bin" / "python"),
        help="Python interpreter used to invoke the SeqSLAM scripts.",
    )
    parser.add_argument(
        "--sim-camera-subdir",
        default="mono_front",
        help="Sim-world camera subdirectory to use.",
    )
    parser.add_argument(
        "--oxford-image-subdir",
        default="stereo/centre",
        help="Oxford image subdirectory to use.",
    )
    parser.add_argument(
        "--skip-sim-worlds",
        action="store_true",
        help="Skip the simulator-world stage.",
    )
    parser.add_argument(
        "--skip-oxford",
        action="store_true",
        help="Skip the Oxford stage.",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Allow the underlying tuning scripts to reuse cached preprocessing/DD artifacts.",
    )
    parser.add_argument(
        "--resume-existing",
        action="store_true",
        help="Reuse an existing bundle directory for continuation runs.",
    )
    return parser.parse_args()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def run_logged_command(command: list[str], cwd: Path, log_path: Path, env: dict[str, str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as log:
        log.write(f"$ {' '.join(command)}\n\n")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log.write(line)
        return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"Command failed ({return_code}): {' '.join(command)}")


def load_first_row(csv_path: Path) -> dict[str, str]:
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        try:
            return next(reader)
        except StopIteration as exc:
            raise RuntimeError(f"No rows found in {csv_path}") from exc


def run_sim_worlds(args: argparse.Namespace, bundle_root: Path, env: dict[str, str]) -> None:
    print("\n" + "=" * 72)
    print("Running sim-world SeqSLAM evaluation")
    print("=" * 72)

    protocol = f"seqslam_full_eval_{args.run_label}_sim_worlds"
    report_subdir = f"SeqSLAM_full_eval_{args.run_label}/sim_worlds_tuning"
    result_tag = f"seqslam_full_eval_{args.run_label}"
    pilot_subdir = f"pilot/seq_slam_{args.run_label}"

    inputs_dir = bundle_root / "inputs"
    sim_pairs_csv = inputs_dir / "sim_world_pairs.csv"
    write_csv(sim_pairs_csv, ["dataset_group", "reference_run", "query_run"], SIM_WORLD_PAIRS)

    tune_cmd = [
        args.python_bin,
        "tune_sim_worlds.py",
        "--pairs-csv",
        str(sim_pairs_csv),
        "--protocol-label",
        protocol,
        "--report-subdir",
        report_subdir,
        "--camera-subdir",
        args.sim_camera_subdir,
        "--result-tag",
        result_tag,
        "--auto-query-stride",
    ]
    if not args.use_cache:
        tune_cmd.append("--no-cache")

    tune_log = bundle_root / "logs" / "sim_worlds_tune.log"
    run_logged_command(tune_cmd, PYSEQSLAM_DIR, tune_log, env)

    sim_summary_csv = REPO_ROOT / "SEQ_SLAM" / "reports" / "sim_worlds" / report_subdir / "summary.csv"
    sim_report_md = REPO_ROOT / "SEQ_SLAM" / "reports" / "sim_worlds" / report_subdir / "report.md"
    evo_report_name = f"seqslam_full_eval_{args.run_label}_sim_worlds_evo"

    evo_cmd = [
        args.python_bin,
        "eval_seqslam_sim_worlds.py",
        "--summary-csv",
        str(sim_summary_csv),
        "--report-name",
        evo_report_name,
        "--camera-subdir-default",
        args.sim_camera_subdir,
        "--pilot-subdir",
        pilot_subdir,
        "--update-cross-model-csvs",
    ]

    evo_log = bundle_root / "logs" / "sim_worlds_evo.log"
    run_logged_command(evo_cmd, PYSEQSLAM_DIR, evo_log, env)

    evo_report = CROSS_MODEL_DIR / f"{evo_report_name}.md"
    package_cmd = [
        args.python_bin,
        str(SCRIPT_DIR / "package_seqslam_results_bundle.py"),
        "--summary-csv",
        str(sim_summary_csv),
        "--seqslam-report",
        str(sim_report_md),
        "--requested-pairs-csv",
        str(sim_pairs_csv),
        "--evo-report",
        str(evo_report),
        "--benchmark-csv",
        str(CROSS_MODEL_DIR / "cross_model_benchmark_results.csv"),
        "--sanity-csv",
        str(CROSS_MODEL_DIR / "cross_model_sanity_results.csv"),
        "--evo-results-root",
        f"SEQ_SLAM/reports/cross_model/{pilot_subdir}",
        "--bundle-dir",
        str(bundle_root / "sim_worlds"),
    ]

    package_log = bundle_root / "logs" / "sim_worlds_package.log"
    run_logged_command(package_cmd, REPO_ROOT, package_log, env)


def run_oxford(args: argparse.Namespace, bundle_root: Path, env: dict[str, str]) -> None:
    print("\n" + "=" * 72)
    print("Running Oxford SeqSLAM tuning")
    print("=" * 72)

    oxford_root = bundle_root / "oxford"
    batch_dir = oxford_root / "01_batch"
    pairs_dir = oxford_root / "03_pairs"
    logs_dir = oxford_root / "logs"
    result_tag = f"seqslam_full_eval_{args.run_label}"

    oxford_pairs_csv = batch_dir / "requested_pairs.csv"
    write_csv(oxford_pairs_csv, ["reference_run", "query_run"], OXFORD_PAIRS)

    artifacts: list[OxfordArtifact] = []
    for pair in OXFORD_PAIRS:
        pair_id = f"{pair['reference_run']}_vs_{pair['query_run']}"
        tune_cmd = [
            args.python_bin,
            "tune_oxford.py",
            "--reference-run",
            pair["reference_run"],
            "--query-run",
            pair["query_run"],
            "--image-subdir",
            args.oxford_image_subdir,
            "--result-tag",
            result_tag,
            "--auto-query-stride",
        ]
        if not args.use_cache:
            tune_cmd.append("--no-cache")

        log_path = logs_dir / f"{pair_id}.log"
        run_logged_command(tune_cmd, PYSEQSLAM_DIR, log_path, env)

        source_result_dir = (
            PYSEQSLAM_DIR
            / "results"
            / "oxford"
            / f"Oxford_{pair['reference_run']}_vs_{pair['query_run']}_{result_tag}"
        )
        best_row = load_first_row(source_result_dir / "tuning_summary.csv")
        artifacts.append(
            OxfordArtifact(
                pair_id=pair_id,
                reference_run=pair["reference_run"],
                query_run=pair["query_run"],
                image_subdir=args.oxford_image_subdir,
                rank_score=float(best_row["rank_score"]),
                valid_ratio=float(best_row["valid_ratio"]),
                corr=float(best_row["corr"]),
                norm_mae=float(best_row["norm_mae"]),
                best_ds=int(best_row["ds"]),
                best_vmin=float(best_row["vmin"]),
                best_vmax=float(best_row["vmax"]),
                best_rwindow=int(best_row["Rwindow"]),
                best_threshold=float(best_row["threshold"]),
                source_result_dir=source_result_dir,
            )
        )

    summary_csv = batch_dir / "summary.csv"
    write_csv(
        summary_csv,
        [
            "pair_id",
            "reference_run",
            "query_run",
            "image_subdir",
            "rank_score",
            "valid_ratio",
            "corr",
            "norm_mae",
            "best_ds",
            "best_vmin",
            "best_vmax",
            "best_rwindow",
            "best_threshold",
            "evo_status",
        ],
        [
            {
                "pair_id": item.pair_id,
                "reference_run": item.reference_run,
                "query_run": item.query_run,
                "image_subdir": item.image_subdir,
                "rank_score": f"{item.rank_score:.6f}",
                "valid_ratio": f"{item.valid_ratio:.6f}",
                "corr": f"{item.corr:.6f}",
                "norm_mae": f"{item.norm_mae:.6f}",
                "best_ds": str(item.best_ds),
                "best_vmin": f"{item.best_vmin:.6f}",
                "best_vmax": f"{item.best_vmax:.6f}",
                "best_rwindow": str(item.best_rwindow),
                "best_threshold": f"{item.best_threshold:.6f}",
                "evo_status": "skipped_no_ground_truth",
            }
            for item in artifacts
        ],
    )

    for item in artifacts:
        pair_bundle_dir = pairs_dir / item.pair_id / "01_seqslam"
        copy_tree(item.source_result_dir, pair_bundle_dir)

    report_lines = [
        "# Oxford SeqSLAM Tuning Bundle",
        "",
        f"Run label: `{args.run_label}`",
        "",
        "## Scope",
        "",
        f"- Front-facing Oxford image path used: `{args.oxford_image_subdir}`",
        "- Reference run: `2014-05-14-13-46-12`",
        "- Query runs: self, `2014-06-23-15-36-04`, `2014-06-26-08-53-56`",
        "- `evo` metrics were not produced for Oxford in this bundle because the current Oxford dataset folders in `SEQ_SLAM/datasets/oxford` do not contain trajectory ground truth files.",
        "",
        "## Best Tuning Rows",
        "",
        "| Pair | Rank | Valid Ratio | Corr | Norm MAE | Best Params |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in artifacts:
        report_lines.append(
            f"| {item.pair_id} | {item.rank_score:.4f} | {item.valid_ratio:.4f} | {item.corr:.4f} | "
            f"{item.norm_mae:.4f} | ds={item.best_ds}, v=({item.best_vmin:.2f},{item.best_vmax:.2f}), "
            f"R={item.best_rwindow}, th={item.best_threshold:.2f} |"
        )
    report_lines.extend(
        [
            "",
            "## Artifact Index",
            "",
        ]
    )
    for item in artifacts:
        report_lines.append(f"- `{(pairs_dir / item.pair_id / '01_seqslam' / 'tuning_summary.csv').relative_to(bundle_root)}`")
        report_lines.append(f"- `{(pairs_dir / item.pair_id / '01_seqslam' / 'oxford_tuning_best_matchings.png').relative_to(bundle_root)}`")

    (batch_dir / "report.md").write_text("\n".join(report_lines))


def write_bundle_readme(args: argparse.Namespace, bundle_root: Path) -> None:
    lines = [
        "# SeqSLAM Full Evaluation Bundle",
        "",
        f"Run label: `{args.run_label}`",
        "",
        "## Layout",
        "",
        "- `inputs/`: pair lists used for the run.",
        "- `logs/`: stage-level command logs.",
        "- `sim_worlds/`: full sim-world tuning + evo bundle ready for cross-model comparison.",
        "- `oxford/`: Oxford tuning bundle. `evo` is intentionally skipped there because trajectory ground truth is not present in the current Oxford dataset folders.",
        "",
        "## Protocol Summary",
        "",
        f"- Sim-world camera: `{args.sim_camera_subdir}`",
        f"- Oxford image path: `{args.oxford_image_subdir}`",
        "- Shared sim-world `evo` policy: raw XY, no alignment, no scale correction, `trans_part` / `angle_deg`, `plot_mode xy`",
        "",
        "## Notes",
        "",
        "- Sim-world results were also written into the shared cross-model sanity and benchmark CSVs.",
        "- Oxford results are tuning-only in this bundle until trajectory ground truth is added.",
        "",
        "## Key Reports",
        "",
        "- `sim_worlds/README.md`",
        "- `oxford/01_batch/report.md`",
    ]
    (bundle_root / "README.md").write_text("\n".join(lines))


def main() -> None:
    args = parse_args()
    python_bin = Path(args.python_bin)
    if not python_bin.exists():
        raise FileNotFoundError(f"Python interpreter not found: {python_bin}")
    args.python_bin = str(python_bin)

    bundle_root = CROSS_MODEL_DIR / f"seqslam_full_eval_{args.run_label}"
    if bundle_root.exists() and not args.resume_existing:
        raise FileExistsError(f"Bundle directory already exists: {bundle_root}")
    bundle_root.mkdir(parents=True, exist_ok=True)
    runtime_dir = bundle_root / ".runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "matplotlib").mkdir(parents=True, exist_ok=True)
    (runtime_dir / "cache").mkdir(parents=True, exist_ok=True)
    run_env = os.environ.copy()
    run_env["MPLCONFIGDIR"] = str(runtime_dir / "matplotlib")
    run_env["XDG_CACHE_HOME"] = str(runtime_dir / "cache")

    try:
        if not args.skip_sim_worlds:
            run_sim_worlds(args, bundle_root, run_env)
        if not args.skip_oxford:
            run_oxford(args, bundle_root, run_env)
        write_bundle_readme(args, bundle_root)
    except Exception:
        print(f"Bundle directory retained for inspection: {bundle_root}", file=sys.stderr)
        raise

    print("\n" + "=" * 72)
    print("SeqSLAM full evaluation bundle created")
    print("=" * 72)
    print(bundle_root)


if __name__ == "__main__":
    main()
