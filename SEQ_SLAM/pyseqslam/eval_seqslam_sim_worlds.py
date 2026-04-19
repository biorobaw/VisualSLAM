"""Export SeqSLAM sim-world matches as TUM trajectories and evaluate with evo.

This script consumes a sim-world tuning summary, recomputes the best-match
sequence for each pair, exports valid matched frames into GT/EST TUM
trajectories, saves a per-frame match/error CSV, runs evo metrics, and writes a
cross-model style report.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path


PYSEQSLAM_DIR = Path(__file__).resolve().parent
SEQ_SLAM_DIR = PYSEQSLAM_DIR.parent
REPO_ROOT = SEQ_SLAM_DIR.parent
CROSS_MODEL_DIR = SEQ_SLAM_DIR / "reports" / "cross_model"
CONVERTER_DIR = CROSS_MODEL_DIR / "scripts"
if str(CONVERTER_DIR) not in sys.path:
    sys.path.insert(0, str(CONVERTER_DIR))

from tune_oxford import _load_timestamps, _split_match_indices
from tune_sim_worlds import _prepare_params_generic
from seqslam import SeqSLAM
from convert_sim_poses_to_tum import yaw_to_quaternion

MODEL_ID = "seq_slam"
OWNER = "SEQ_SLAM lane"
TRAJECTORY_FORMAT = "TUM"
ALIGNMENT = "raw_xy_no_alignment"
SYNC_TOLERANCE = "NA"
FPS = 10.0
DATE_STR = date.today().isoformat()


@dataclass
class SummaryRow:
    dataset_group: str
    reference_run: str
    query_run: str
    camera_subdir: str
    protocol: str
    best_ds: int
    best_vmin: float
    best_vmax: float
    best_rwindow: int
    best_threshold: float
    valid_count: int
    invalid_count: int
    valid_ratio: float
    corr: float
    norm_mae: float
    rank_score: float
    tuning_pass: bool


@dataclass
class EvalArtifacts:
    summary: SummaryRow
    sequence_id: str
    pair_dir: Path
    gt_tum: Path
    est_tum: Path
    matches_csv: Path
    num_eval_poses: int
    ape_rmse: float
    rpe_trans_rmse: float
    rpe_rot_rmse: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SeqSLAM sim-world matches with evo")
    parser.add_argument("--summary-csv", required=True, help="Summary CSV emitted by tune_sim_worlds.py")
    parser.add_argument(
        "--report-name",
        default=f"seqslam_sim_worlds_match_eval_{DATE_STR}",
        help="Basename for the markdown report under reports/cross_model",
    )
    parser.add_argument(
        "--update-cross-model-csvs",
        action="store_true",
        help="Append/update cross_model_sanity_results.csv and cross_model_benchmark_results.csv",
    )
    parser.add_argument(
        "--camera-subdir-default",
        default="mono_front",
        help="Fallback camera subdirectory when older summary CSVs do not include camera_subdir.",
    )
    parser.add_argument(
        "--pilot-subdir",
        default="pilot/seq_slam",
        help="Subdirectory under reports/cross_model where per-pair TUM/evo artifacts are written.",
    )
    return parser.parse_args()


def load_summary_rows(path: Path, default_camera_subdir: str) -> list[SummaryRow]:
    rows: list[SummaryRow] = []
    with path.open(newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            rows.append(
                SummaryRow(
                    dataset_group=row["dataset_group"],
                    reference_run=row["reference_run"],
                    query_run=row["query_run"],
                    camera_subdir=(row.get("camera_subdir") or default_camera_subdir).strip(),
                    protocol=row["protocol"],
                    best_ds=int(row["best_ds"]),
                    best_vmin=float(row["best_vmin"]),
                    best_vmax=float(row["best_vmax"]),
                    best_rwindow=int(row["best_rwindow"]),
                    best_threshold=float(row["best_threshold"]),
                    valid_count=int(row["valid_count"]),
                    invalid_count=int(row["invalid_count"]),
                    valid_ratio=float(row["valid_ratio"]),
                    corr=float(row["corr"]),
                    norm_mae=float(row["norm_mae"]),
                    rank_score=float(row["rank_score"]),
                    tuning_pass=row["tuning_pass"].strip().lower() == "true",
                )
            )
    if not rows:
        raise RuntimeError(f"No rows found in {path}")
    return rows


def load_pose_map(csv_path: Path) -> dict[int, dict[str, float]]:
    pose_map: dict[int, dict[str, float]] = {}
    with csv_path.open(newline="") as fp:
        reader = csv.DictReader(fp)
        required = {"frame_id", "x", "y", "yaw_rad"}
        fields = set(reader.fieldnames or [])
        if not required.issubset(fields):
            raise RuntimeError(f"Missing required columns in {csv_path}: {sorted(required)}")
        for row in reader:
            frame_id = int(row["frame_id"])
            pose_map[frame_id] = {
                "x": float(row["x"]),
                "y": float(row["y"]),
                "yaw_rad": float(row["yaw_rad"]),
            }
    return pose_map


def sequence_id_for(row: SummaryRow) -> str:
    return f"{row.reference_run}_vs_{row.query_run}"


def run_best_matches(row: SummaryRow):
    params, reference_path, query_path, _n_ref_images, _n_qry_raw, _n_qry_used, _stride = _prepare_params_generic(
        row.dataset_group,
        row.reference_run,
        row.query_run,
        camera_subdir=row.camera_subdir,
        use_cache=True,
        query_stride=1,
        auto_query_stride=True,
    )
    params.DO_FIND_MATCHES = 0
    ss = SeqSLAM(params)
    try:
        results = ss.run()
    except AttributeError as exc:
        if "results_preprocessing" in str(exc):
            params, reference_path, query_path, _n_ref_images, _n_qry_raw, _n_qry_used, _stride = _prepare_params_generic(
                row.dataset_group,
                row.reference_run,
                row.query_run,
                use_cache=False,
                query_stride=1,
                auto_query_stride=True,
            )
            params.DO_FIND_MATCHES = 0
            ss = SeqSLAM(params)
            results = ss.run()
        else:
            raise
    ss.params.matching.ds = row.best_ds
    ss.params.matching.vmin = row.best_vmin
    ss.params.matching.vmax = row.best_vmax
    ss.params.matching.Rwindow = row.best_rwindow
    matches = ss.getMatches(results.DD)
    ref_images, ref_timestamps = _load_timestamps(reference_path)
    qry_images, qry_timestamps = _load_timestamps(query_path)
    if len(qry_timestamps) > len(ref_timestamps):
        stride = max(1, int(round(len(qry_timestamps) / float(len(ref_timestamps)))))
        qry_timestamps = qry_timestamps[::stride]
    return matches, ref_timestamps, qry_timestamps


def write_tum_row(out, timestamp: float, pose: dict[str, float]) -> None:
    qx, qy, qz, qw = yaw_to_quaternion(pose["yaw_rad"])
    out.write(
        f"{timestamp:.6f} {pose['x']:.6f} {pose['y']:.6f} 0.000000 "
        f"{qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n"
    )


def export_pair(row: SummaryRow, pilot_root: Path) -> tuple[Path, Path, Path, int]:
    sequence_id = sequence_id_for(row)
    pair_dir = pilot_root / sequence_id
    inputs_dir = pair_dir / "inputs"
    outputs_dir = pair_dir / "outputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    matches, ref_timestamps, qry_timestamps = run_best_matches(row)
    match_idx, quality, valid_mask, _invalid_mask = _split_match_indices(matches, threshold=row.best_threshold)

    ref_pose_map = load_pose_map(SEQ_SLAM_DIR / "datasets" / row.dataset_group / row.reference_run / "poses.csv")
    qry_pose_map = load_pose_map(SEQ_SLAM_DIR / "datasets" / row.dataset_group / row.query_run / "poses.csv")

    gt_tum = inputs_dir / f"{row.query_run}_gt_from_query.tum.txt"
    est_tum = inputs_dir / f"{row.reference_run}_est_from_matches.tum.txt"
    matches_csv = outputs_dir / "matched_frames.csv"

    eval_rows: list[dict[str, str]] = []
    num_eval_poses = 0
    with gt_tum.open("w") as gt_out, est_tum.open("w") as est_out:
        for query_array_idx, query_frame_id in enumerate(qry_timestamps):
            matched_ref_idx = int(round(match_idx[query_array_idx])) if query_array_idx < len(match_idx) and valid_mask[query_array_idx] else -1
            valid = bool(query_array_idx < len(valid_mask) and valid_mask[query_array_idx])
            ref_frame_id = ref_timestamps[matched_ref_idx] if valid and 0 <= matched_ref_idx < len(ref_timestamps) else -1

            gt_pose = qry_pose_map[int(query_frame_id)]
            if valid:
                est_pose = ref_pose_map[int(ref_frame_id)]
                timestamp = (int(query_frame_id) - 1) / FPS
                write_tum_row(gt_out, timestamp, gt_pose)
                write_tum_row(est_out, timestamp, est_pose)
                xy_error = ((gt_pose["x"] - est_pose["x"]) ** 2 + (gt_pose["y"] - est_pose["y"]) ** 2) ** 0.5
                num_eval_poses += 1
            else:
                est_pose = {"x": "", "y": "", "yaw_rad": ""}
                xy_error = ""

            eval_rows.append(
                {
                    "query_array_index": str(query_array_idx),
                    "query_frame_id": str(query_frame_id),
                    "matched_ref_index": str(matched_ref_idx),
                    "matched_ref_frame_id": str(ref_frame_id),
                    "quality": "" if query_array_idx >= len(quality) else f"{quality[query_array_idx]:.9f}",
                    "valid": str(valid),
                    "gt_x": f"{gt_pose['x']:.6f}",
                    "gt_y": f"{gt_pose['y']:.6f}",
                    "gt_yaw_rad": f"{gt_pose['yaw_rad']:.9f}",
                    "est_x": "" if not valid else f"{est_pose['x']:.6f}",
                    "est_y": "" if not valid else f"{est_pose['y']:.6f}",
                    "est_yaw_rad": "" if not valid else f"{est_pose['yaw_rad']:.9f}",
                    "xy_error": "" if not valid else f"{xy_error:.6f}",
                }
            )

    with matches_csv.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "query_array_index",
                "query_frame_id",
                "matched_ref_index",
                "matched_ref_frame_id",
                "quality",
                "valid",
                "gt_x",
                "gt_y",
                "gt_yaw_rad",
                "est_x",
                "est_y",
                "est_yaw_rad",
                "xy_error",
            ],
        )
        writer.writeheader()
        writer.writerows(eval_rows)

    return gt_tum, est_tum, matches_csv, num_eval_poses


def parse_rmse(stdout: str) -> float:
    match = re.search(r"^\s*rmse\s+([0-9.eE+-]+)\s*$", stdout, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Unable to parse rmse from evo output:\n{stdout}")
    return float(match.group(1))


@contextmanager
def headless_evo_env():
    settings_src = Path.home() / ".evo" / "settings.json"
    with tempfile.TemporaryDirectory(prefix="seqslam_match_eval_") as temp_home:
        evo_dir = Path(temp_home) / ".evo"
        evo_dir.mkdir(parents=True, exist_ok=True)
        settings = json.loads(settings_src.read_text()) if settings_src.exists() else {}
        settings["plot_backend"] = "Agg"
        (evo_dir / "settings.json").write_text(json.dumps(settings, indent=4))
        env = os.environ.copy()
        env["HOME"] = temp_home
        python_bin_dir = str(Path(sys.executable).parent)
        env["PATH"] = f"{python_bin_dir}:{env.get('PATH', '')}"
        yield env


def resolve_evo_executable(name: str) -> str:
    """Resolve evo CLI from active environment before falling back to PATH."""
    candidate_dirs = [Path(sys.executable).parent, Path(sys.prefix) / "bin"]
    for bin_dir in candidate_dirs:
        candidate = bin_dir / name
        if candidate.exists():
            return str(candidate)
    discovered = shutil.which(name)
    if discovered:
        return discovered
    raise FileNotFoundError(
        f"Required executable '{name}' was not found in {[str(d) for d in candidate_dirs]} or PATH. "
        "Install evo in the active Python environment."
    )


def run_evo(command: list[str], txt_path: Path, env: dict[str, str]) -> float:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    combined = completed.stdout
    if completed.stderr:
        combined = f"{combined}\n{completed.stderr}".strip() + "\n"
    txt_path.write_text(combined)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{combined}")
    return parse_rmse(completed.stdout)


def evaluate_pair(row: SummaryRow, gt_tum: Path, est_tum: Path, pilot_root: Path) -> tuple[float, float, float]:
    sequence_id = sequence_id_for(row)
    outputs_dir = pilot_root / sequence_id / "outputs"
    evo_ape = resolve_evo_executable("evo_ape")
    evo_rpe = resolve_evo_executable("evo_rpe")
    with headless_evo_env() as env:
        ape_rmse = run_evo(
            [
                evo_ape,
                "tum",
                str(gt_tum),
                str(est_tum),
                "-r",
                "trans_part",
                "--project_to_plane",
                "xy",
                "--save_results",
                str(outputs_dir / "ape_trans_xy_raw.zip"),
                "--save_plot",
                str(outputs_dir / "ape_trans_xy_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            outputs_dir / "ape_trans_xy_raw.txt",
            env,
        )
        rpe_trans_rmse = run_evo(
            [
                evo_rpe,
                "tum",
                str(gt_tum),
                str(est_tum),
                "-r",
                "trans_part",
                "--project_to_plane",
                "xy",
                "--save_results",
                str(outputs_dir / "rpe_trans_xy_raw.zip"),
                "--save_plot",
                str(outputs_dir / "rpe_trans_xy_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            outputs_dir / "rpe_trans_xy_raw.txt",
            env,
        )
        rpe_rot_rmse = run_evo(
            [
                evo_rpe,
                "tum",
                str(gt_tum),
                str(est_tum),
                "-r",
                "angle_deg",
                "--save_results",
                str(outputs_dir / "rpe_rot_raw.zip"),
                "--save_plot",
                str(outputs_dir / "rpe_rot_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            outputs_dir / "rpe_rot_raw.txt",
            env,
        )
    return ape_rmse, rpe_trans_rmse, rpe_rot_rmse


def upsert_csv_row(csv_path: Path, row: dict[str, str]) -> None:
    with csv_path.open(newline="") as fp:
        reader = csv.DictReader(fp)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError(f"Missing CSV header in {csv_path}")
        rows = list(reader)

    key = (row["date"], row["sequence_id"], row["protocol_label"])
    replaced = False
    for idx, existing in enumerate(rows):
        if (existing["date"], existing["sequence_id"], existing["protocol_label"]) == key:
            rows[idx] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)

    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_cross_model_csvs(artifacts: list[EvalArtifacts]) -> None:
    sanity_csv = CROSS_MODEL_DIR / "cross_model_sanity_results.csv"
    benchmark_csv = CROSS_MODEL_DIR / "cross_model_benchmark_results.csv"
    for item in artifacts:
        identity = item.summary.reference_run == item.summary.query_run
        protocol_label = f"seqslam_match_export_{item.summary.protocol}"
        notes = (
            f"SeqSLAM best params ds={item.summary.best_ds}, "
            f"v=({item.summary.best_vmin:.2f},{item.summary.best_vmax:.2f}), "
            f"R={item.summary.best_rwindow}, th={item.summary.best_threshold:.2f}; "
            f"valid_ratio={item.summary.valid_ratio:.4f}, corr={item.summary.corr:.4f}"
        )
        row = {
            "date": DATE_STR,
            "sequence_id": item.sequence_id,
            "model_id": MODEL_ID,
            "owner": OWNER,
            "protocol_label": protocol_label,
            "eval_mode": "sanity_selfcheck" if identity else "seqslam_place_match_eval",
            "trajectory_format": TRAJECTORY_FORMAT,
            "valid_input": "True",
            "ate_rmse": f"{item.ape_rmse:.6f}",
            "rpe_trans_rmse": f"{item.rpe_trans_rmse:.6f}",
            "rpe_rot_rmse": f"{item.rpe_rot_rmse:.6f}",
            "num_poses": str(item.num_eval_poses),
            "alignment": ALIGNMENT,
            "sync_tolerance_sec": SYNC_TOLERANCE,
            "notes": notes,
        }
        target = sanity_csv if identity else benchmark_csv
        upsert_csv_row(target, row)


def write_report(report_path: Path, artifacts: list[EvalArtifacts], summary_csv: Path) -> None:
    camera_paths = sorted({item.summary.camera_subdir for item in artifacts})
    lines = [
        "# SeqSLAM Sim-World Match Evaluation",
        "",
        f"Date: {DATE_STR}",
        "",
        "## Scope",
        "",
        f"- Source tuning summary: `{summary_csv.relative_to(REPO_ROOT)}`",
        f"- Camera subdirectory(s): `{', '.join(camera_paths)}`",
        "- For each pair, recompute the best-match sequence from SeqSLAM using the selected tuning row.",
        "- Export GT query poses and matched reference poses into synchronized TUM trajectories on valid matched frames only.",
        "- Run raw `evo` translation/rotation metrics without alignment because the simulator trajectories already share a coordinate frame.",
        "",
        "## Results",
        "",
        "| Sequence | Valid Ratio | Corr | Eval Poses | APE XY RMSE | RPE XY RMSE | RPE Rot RMSE | Pair Dir |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in artifacts:
        lines.append(
            f"| {item.sequence_id} | {item.summary.valid_ratio:.4f} | {item.summary.corr:.4f} | "
            f"{item.num_eval_poses} | {item.ape_rmse:.6f} | {item.rpe_trans_rmse:.6f} | "
            f"{item.rpe_rot_rmse:.6f} | `{item.pair_dir.relative_to(REPO_ROOT)}` |"
        )

    lines.extend(
        [
            "",
            "## Artifact Index",
            "",
        ]
    )
    for item in artifacts:
        lines.extend(
            [
                f"- `{item.matches_csv.relative_to(REPO_ROOT)}`",
                f"- `{item.gt_tum.relative_to(REPO_ROOT)}`",
                f"- `{item.est_tum.relative_to(REPO_ROOT)}`",
                f"- `{(item.pair_dir / 'outputs' / 'ape_trans_xy_raw.pdf').relative_to(REPO_ROOT)}`",
                f"- `{(item.pair_dir / 'outputs' / 'rpe_trans_xy_raw.pdf').relative_to(REPO_ROOT)}`",
                f"- `{(item.pair_dir / 'outputs' / 'rpe_rot_raw.pdf').relative_to(REPO_ROOT)}`",
            ]
        )
    report_path.write_text("\n".join(lines))


def main() -> None:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    pilot_root = CROSS_MODEL_DIR / args.pilot_subdir
    rows = load_summary_rows(summary_csv, args.camera_subdir_default)
    artifacts: list[EvalArtifacts] = []

    for row in rows:
        gt_tum, est_tum, matches_csv, num_eval_poses = export_pair(row, pilot_root)
        ape_rmse, rpe_trans_rmse, rpe_rot_rmse = evaluate_pair(row, gt_tum, est_tum, pilot_root)
        sequence_id = sequence_id_for(row)
        pair_dir = pilot_root / sequence_id
        artifacts.append(
            EvalArtifacts(
                summary=row,
                sequence_id=sequence_id,
                pair_dir=pair_dir,
                gt_tum=gt_tum,
                est_tum=est_tum,
                matches_csv=matches_csv,
                num_eval_poses=num_eval_poses,
                ape_rmse=ape_rmse,
                rpe_trans_rmse=rpe_trans_rmse,
                rpe_rot_rmse=rpe_rot_rmse,
            )
        )

    if args.update_cross_model_csvs:
        update_cross_model_csvs(artifacts)

    report_path = CROSS_MODEL_DIR / f"{args.report_name}.md"
    write_report(report_path, artifacts, summary_csv)

    print(f"Completed {len(artifacts)} SeqSLAM match evaluations.")
    print(f"Report: {report_path}")
    for item in artifacts:
        print(
            f"{item.sequence_id}: valid_ratio={item.summary.valid_ratio:.4f}, "
            f"APE={item.ape_rmse:.6f}, RPE_trans={item.rpe_trans_rmse:.6f}, "
            f"RPE_rot={item.rpe_rot_rmse:.6f}"
        )


if __name__ == "__main__":
    main()
