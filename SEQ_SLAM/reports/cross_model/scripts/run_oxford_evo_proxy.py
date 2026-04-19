#!/usr/bin/env python3
"""Run Oxford SeqSLAM evo for one pair or a batch of pairs.

Supports:
- Proxy mode: reuse one TUM trajectory for both reference/query pose sampling.
- GT mode: use per-run ground-truth TUM mapping from a CSV file.

The script reconstructs best SeqSLAM matches for each pair, exports aligned
GT/EST TUM trajectories on valid matched frames, runs evo metrics, and writes
per-pair plus batch-level summaries.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation


SCRIPT_DIR = Path(__file__).resolve().parent
CROSS_MODEL_DIR = SCRIPT_DIR.parent
SEQ_SLAM_DIR = CROSS_MODEL_DIR.parent.parent
PYSEQSLAM_DIR = SEQ_SLAM_DIR / "pyseqslam"
REPO_ROOT = SEQ_SLAM_DIR.parent

import sys

if str(PYSEQSLAM_DIR) not in sys.path:
    sys.path.insert(0, str(PYSEQSLAM_DIR))

from tune_oxford import _prepare_params, _split_match_indices
from seqslam import SeqSLAM


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Oxford SeqSLAM evo in proxy or GT mode")
    parser.add_argument("--run-label", required=True, help="Existing bundle run label, e.g. 2026-04-17_run1")
    parser.add_argument("--reference-run")
    parser.add_argument("--query-run")
    parser.add_argument(
        "--pairs-csv",
        help="CSV with columns reference_run,query_run for batch processing.",
    )
    parser.add_argument("--image-subdir", default="stereo/centre")
    parser.add_argument("--result-tag", required=True, help="Suffix used in SeqSLAM result directory")
    parser.add_argument("--proxy-traj", help="TUM trajectory used as surrogate pose source")
    parser.add_argument(
        "--proxy-time-alignment",
        choices=["absolute", "normalized"],
        default="absolute",
        help=(
            "How to align run image timestamps to proxy trajectory time in proxy mode. "
            "'absolute' uses raw Unix timestamps; 'normalized' maps each run timeline to [0,1] "
            "then to proxy trajectory span."
        ),
    )
    parser.add_argument(
        "--gt-map-csv",
        help="CSV with columns run_id,gt_tum for real GT mode.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "proxy", "gt"],
        default="auto",
        help="Evaluation mode. auto prefers GT if mapping is available else proxy.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue batch processing when a pair fails.",
    )
    parser.add_argument("--min-exported-poses", type=int, default=20)
    return parser.parse_args()


@dataclass
class PairSpec:
    reference_run: str
    query_run: str

    @property
    def pair_id(self) -> str:
        return f"{self.reference_run}_vs_{self.query_run}"


@dataclass
class PairResult:
    pair_id: str
    mode: str
    status: str
    exported_poses: int
    output_root: Path
    message: str


def load_best_row(summary_csv: Path) -> dict[str, str]:
    with summary_csv.open(newline="") as fp:
        row = next(csv.DictReader(fp), None)
    if row is None:
        raise RuntimeError(f"No rows found in {summary_csv}")
    return row


def load_pairs(args: argparse.Namespace) -> list[PairSpec]:
    if args.pairs_csv:
        pairs: list[PairSpec] = []
        with resolve_repo_path(args.pairs_csv).open(newline="") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                ref = (row.get("reference_run") or "").strip()
                qry = (row.get("query_run") or "").strip()
                if ref and qry:
                    pairs.append(PairSpec(reference_run=ref, query_run=qry))
        if not pairs:
            raise RuntimeError(f"No pairs found in {args.pairs_csv}")
        return pairs

    if not args.reference_run or not args.query_run:
        raise RuntimeError("Either --pairs-csv or both --reference-run and --query-run must be provided")
    return [PairSpec(reference_run=args.reference_run, query_run=args.query_run)]


def load_gt_map(path: str | None) -> dict[str, Path]:
    if not path:
        return {}
    mapping: dict[str, Path] = {}
    with resolve_repo_path(path).open(newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            run_id = (row.get("run_id") or "").strip()
            gt_tum = (row.get("gt_tum") or "").strip()
            if not run_id or not gt_tum:
                continue
            mapping[run_id] = resolve_repo_path(gt_tum)
    return mapping


def run_seqslam_best_matches(reference_run: str, query_run: str, image_subdir: str, best_row: dict[str, str]):
    ds = int(best_row["ds"])
    vmin = float(best_row["vmin"])
    vmax = float(best_row["vmax"])
    rwindow = int(best_row["Rwindow"])

    def _run(use_cache: bool):
        params, *_ = _prepare_params(
            reference_run,
            query_run,
            image_subdir=image_subdir,
            use_cache=use_cache,
            query_stride=1,
            auto_query_stride=True,
        )
        params.DO_FIND_MATCHES = 0
        ss = SeqSLAM(params)
        results = ss.run()
        ss.params.matching.ds = ds
        ss.params.matching.vmin = vmin
        ss.params.matching.vmax = vmax
        ss.params.matching.Rwindow = rwindow
        matches = ss.getMatches(results.DD)
        return params, matches

    try:
        return _run(use_cache=True)
    except AttributeError as exc:
        if "results_preprocessing" in str(exc):
            return _run(use_cache=False)
        raise


def load_proxy_trajectory(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    t: list[float] = []
    pos: list[tuple[float, float, float]] = []
    quat: list[tuple[float, float, float, float]] = []
    with path.open() as fp:
        for line in fp:
            parts = line.strip().split()
            if len(parts) != 8:
                continue
            t.append(float(parts[0]))
            pos.append((float(parts[1]), float(parts[2]), float(parts[3])))
            quat.append((float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])))
    if len(t) < 2:
        raise RuntimeError(f"Proxy trajectory has insufficient poses: {path}")
    ts = np.asarray(t, dtype=float)
    xyz = np.asarray(pos, dtype=float)
    yaw = Rotation.from_quat(np.asarray(quat, dtype=float)).as_euler("xyz", degrees=False)[:, 2]
    return ts, xyz, yaw


def load_tum_trajectory(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(f"Missing trajectory file: {path}")
    return load_proxy_trajectory(path)


def interpolate_pose(ts: float, src_t: np.ndarray, src_xyz: np.ndarray, src_yaw: np.ndarray):
    if ts < src_t[0] or ts > src_t[-1]:
        return None
    idx = int(np.searchsorted(src_t, ts))
    if idx <= 0:
        i0 = i1 = 0
    elif idx >= len(src_t):
        i0 = i1 = len(src_t) - 1
    else:
        i0, i1 = idx - 1, idx

    if i0 == i1 or src_t[i1] == src_t[i0]:
        alpha = 0.0
    else:
        alpha = (ts - src_t[i0]) / (src_t[i1] - src_t[i0])

    xyz = src_xyz[i0] * (1.0 - alpha) + src_xyz[i1] * alpha
    yaw = src_yaw[i0] * (1.0 - alpha) + src_yaw[i1] * alpha
    sy = math.sin(yaw * 0.5)
    cy = math.cos(yaw * 0.5)
    return xyz[0], xyz[1], xyz[2], 0.0, 0.0, sy, cy


def to_proxy_time_absolute(ts_us: int, _run_ts_us: np.ndarray, _proxy_t: np.ndarray) -> float:
    return ts_us / 1e6


def to_proxy_time_normalized(ts_us: int, run_ts_us: np.ndarray, proxy_t: np.ndarray) -> float:
    if len(run_ts_us) < 2 or run_ts_us[-1] <= run_ts_us[0]:
        return float(proxy_t[0])
    alpha = (float(ts_us) - float(run_ts_us[0])) / (float(run_ts_us[-1]) - float(run_ts_us[0]))
    alpha = min(1.0, max(0.0, alpha))
    return float(proxy_t[0]) + alpha * float(proxy_t[-1] - proxy_t[0])


def resolve_evo(name: str) -> str:
    candidate = Path(sys.executable).parent / name
    if candidate.exists():
        return str(candidate)
    discovered = shutil.which(name)
    if discovered:
        return discovered
    raise FileNotFoundError(f"Could not locate {name}")


@contextmanager
def headless_evo_env():
    settings_src = Path.home() / ".evo" / "settings.json"
    with tempfile.TemporaryDirectory(prefix="seqslam_oxford_evo_proxy_") as temp_home:
        evo_dir = Path(temp_home) / ".evo"
        evo_dir.mkdir(parents=True, exist_ok=True)
        settings = json.loads(settings_src.read_text()) if settings_src.exists() else {}
        settings["plot_backend"] = "Agg"
        (evo_dir / "settings.json").write_text(json.dumps(settings, indent=4))
        env = os.environ.copy()
        env["HOME"] = temp_home
        env["PATH"] = f"{Path(sys.executable).parent}:{env.get('PATH', '')}"
        yield env


def run_evo(cmd: list[str], output_txt: Path, env: dict[str, str]) -> None:
    completed = subprocess.run(cmd, cwd=REPO_ROOT, env=env, text=True, capture_output=True, check=False)
    text = completed.stdout
    if completed.stderr:
        text = (text + "\n" + completed.stderr).strip() + "\n"
    output_txt.write_text(text)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(cmd)}\n{text}")


def parse_rmse(text: str) -> float | None:
    match = re.search(r"^\s*rmse\s+([0-9.eE+-]+)\s*$", text, re.MULTILINE)
    if not match:
        return None
    return float(match.group(1))


def write_batch_summary(batch_dir: Path, rows: list[PairResult]) -> None:
    batch_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = batch_dir / "summary.csv"
    with summary_csv.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["pair_id", "mode", "status", "exported_poses", "output_root", "message"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "pair_id": row.pair_id,
                    "mode": row.mode,
                    "status": row.status,
                    "exported_poses": str(row.exported_poses),
                    "output_root": str(row.output_root),
                    "message": row.message,
                }
            )

    report = batch_dir / "report.md"
    lines = [
        "# Oxford Evo Batch Summary",
        "",
        "| Pair | Mode | Status | Exported Poses | Notes |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.pair_id} | {row.mode} | {row.status} | {row.exported_poses} | {row.message} |"
        )
    report.write_text("\n".join(lines))


def choose_mode(args: argparse.Namespace, gt_map: dict[str, Path], pair: PairSpec) -> str:
    if args.mode == "proxy":
        return "proxy"
    if args.mode == "gt":
        return "gt"
    if pair.reference_run in gt_map and pair.query_run in gt_map:
        return "gt"
    return "proxy"


def run_pair(
    args: argparse.Namespace,
    pair: PairSpec,
    gt_map: dict[str, Path],
    evo_ape: str,
    evo_rpe: str,
) -> PairResult:
    mode = choose_mode(args, gt_map, pair)

    source_summary = (
        PYSEQSLAM_DIR
        / "results"
        / "oxford"
        / f"Oxford_{pair.reference_run}_vs_{pair.query_run}_{args.result_tag}"
        / "tuning_summary.csv"
    )
    if not source_summary.exists():
        return PairResult(pair.pair_id, mode, "failed", 0, Path(""), f"Missing tuning summary: {source_summary}")

    output_subdir = "02_evo_gt" if mode == "gt" else "02_evo_proxy"
    output_root = (
        CROSS_MODEL_DIR
        / f"seqslam_full_eval_{args.run_label}"
        / "oxford"
        / "03_pairs"
        / pair.pair_id
        / output_subdir
    )
    output_root.mkdir(parents=True, exist_ok=True)

    best = load_best_row(source_summary)
    threshold = float(best["threshold"])
    params, matches = run_seqslam_best_matches(pair.reference_run, pair.query_run, args.image_subdir, best)
    match_idx, quality, valid_mask, _invalid_mask = _split_match_indices(matches, threshold=threshold)

    ref_ts = np.asarray(params.dataset[0].imageIndices, dtype=np.int64)
    qry_ts = np.asarray(params.dataset[1].imageIndices, dtype=np.int64)

    if mode == "gt":
        if pair.reference_run not in gt_map or pair.query_run not in gt_map:
            return PairResult(pair.pair_id, mode, "failed", 0, output_root, "Missing GT map entry for one or both runs")
        ref_t, ref_xyz, ref_yaw = load_tum_trajectory(gt_map[pair.reference_run])
        qry_t, qry_xyz, qry_yaw = load_tum_trajectory(gt_map[pair.query_run])
        ref_time_mapper = to_proxy_time_absolute
        qry_time_mapper = to_proxy_time_absolute
    else:
        if not args.proxy_traj:
            return PairResult(pair.pair_id, mode, "failed", 0, output_root, "Proxy mode requires --proxy-traj")
        proxy_traj = resolve_repo_path(args.proxy_traj)
        if not proxy_traj.exists():
            return PairResult(pair.pair_id, mode, "failed", 0, output_root, f"Missing proxy trajectory: {proxy_traj}")
        ref_t, ref_xyz, ref_yaw = load_proxy_trajectory(proxy_traj)
        qry_t, qry_xyz, qry_yaw = ref_t, ref_xyz, ref_yaw
        if args.proxy_time_alignment == "normalized":
            ref_time_mapper = to_proxy_time_normalized
            qry_time_mapper = to_proxy_time_normalized
        else:
            ref_time_mapper = to_proxy_time_absolute
            qry_time_mapper = to_proxy_time_absolute

    gt_tum = output_root / ("query_gt.tum.txt" if mode == "gt" else "query_gt_proxy.tum.txt")
    est_tum = output_root / ("matched_ref_est.tum.txt" if mode == "gt" else "matched_ref_proxy_est.tum.txt")
    matched_csv = output_root / "matched_frames.csv"

    exported = 0
    rows: list[dict[str, str]] = []
    with gt_tum.open("w") as gt_fp, est_tum.open("w") as est_fp:
        for qi, q_us in enumerate(qry_ts):
            if qi >= len(valid_mask) or not bool(valid_mask[qi]):
                continue
            ri = int(round(match_idx[qi]))
            if ri < 0 or ri >= len(ref_ts):
                continue

            q_proxy_sec = qry_time_mapper(int(q_us), qry_ts, qry_t)
            r_proxy_sec = ref_time_mapper(int(ref_ts[ri]), ref_ts, ref_t)
            q_pose = interpolate_pose(q_proxy_sec, qry_t, qry_xyz, qry_yaw)
            r_pose = interpolate_pose(r_proxy_sec, ref_t, ref_xyz, ref_yaw)
            if q_pose is None or r_pose is None:
                continue

            t_out = exported / 10.0
            gt_fp.write(
                f"{t_out:.6f} {q_pose[0]:.6f} {q_pose[1]:.6f} {q_pose[2]:.6f} "
                f"{q_pose[3]:.9f} {q_pose[4]:.9f} {q_pose[5]:.9f} {q_pose[6]:.9f}\n"
            )
            est_fp.write(
                f"{t_out:.6f} {r_pose[0]:.6f} {r_pose[1]:.6f} {r_pose[2]:.6f} "
                f"{r_pose[3]:.9f} {r_pose[4]:.9f} {r_pose[5]:.9f} {r_pose[6]:.9f}\n"
            )
            rows.append(
                {
                    "query_index": str(qi),
                    "reference_index": str(ri),
                    "query_timestamp_sec": f"{q_us / 1e6:.6f}",
                    "reference_timestamp_sec": f"{ref_ts[ri] / 1e6:.6f}",
                    "query_proxy_sec": f"{q_proxy_sec:.6f}",
                    "reference_proxy_sec": f"{r_proxy_sec:.6f}",
                    "quality": f"{float(quality[qi]):.9f}",
                }
            )
            exported += 1

    with matched_csv.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "query_index",
                "reference_index",
                "query_timestamp_sec",
                "reference_timestamp_sec",
                "query_proxy_sec",
                "reference_proxy_sec",
                "quality",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    if exported < args.min_exported_poses:
        return PairResult(
            pair.pair_id,
            mode,
            "failed",
            exported,
            output_root,
            f"Only {exported} overlapping poses; expected at least {args.min_exported_poses}",
        )

    with headless_evo_env() as evo_env:
        run_evo(
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
                str(output_root / "ape_trans_xy_raw.zip"),
                "--save_plot",
                str(output_root / "ape_trans_xy_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            output_root / "ape_trans_xy_raw.txt",
            evo_env,
        )
        run_evo(
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
                str(output_root / "rpe_trans_xy_raw.zip"),
                "--save_plot",
                str(output_root / "rpe_trans_xy_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            output_root / "rpe_trans_xy_raw.txt",
            evo_env,
        )
        run_evo(
            [
                evo_rpe,
                "tum",
                str(gt_tum),
                str(est_tum),
                "-r",
                "angle_deg",
                "--save_results",
                str(output_root / "rpe_rot_raw.zip"),
                "--save_plot",
                str(output_root / "rpe_rot_raw.pdf"),
                "--plot_mode",
                "xy",
                "--no_warnings",
            ],
            output_root / "rpe_rot_raw.txt",
            evo_env,
        )

    ape_rmse = parse_rmse((output_root / "ape_trans_xy_raw.txt").read_text())
    rpe_rmse = parse_rmse((output_root / "rpe_trans_xy_raw.txt").read_text())
    rpe_rot_rmse = parse_rmse((output_root / "rpe_rot_raw.txt").read_text())
    readme = output_root / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# Oxford SeqSLAM Evo ({mode.upper()})",
                "",
                f"Pair: {pair.pair_id}",
                f"Mode: {mode}",
                f"Proxy time alignment: {args.proxy_time_alignment if mode == 'proxy' else 'n/a'}",
                f"Exported synchronized poses: {exported}",
                f"APE trans xy rmse: {ape_rmse if ape_rmse is not None else 'n/a'}",
                f"RPE trans xy rmse: {rpe_rmse if rpe_rmse is not None else 'n/a'}",
                f"RPE rot rmse (deg): {rpe_rot_rmse if rpe_rot_rmse is not None else 'n/a'}",
            ]
        )
    )

    return PairResult(pair.pair_id, mode, "ok", exported, output_root, "evo completed")


def main() -> None:
    args = parse_args()

    # tune_oxford/_prepare_params use project-relative dataset paths.
    os.chdir(PYSEQSLAM_DIR)

    pairs = load_pairs(args)
    gt_map = load_gt_map(args.gt_map_csv)

    evo_ape = resolve_evo("evo_ape")
    evo_rpe = resolve_evo("evo_rpe")

    results: list[PairResult] = []
    for pair in pairs:
        try:
            result = run_pair(args, pair, gt_map, evo_ape, evo_rpe)
        except Exception as exc:
            result = PairResult(pair.pair_id, args.mode, "failed", 0, Path(""), str(exc))

        results.append(result)
        print(
            json.dumps(
                {
                    "pair_id": result.pair_id,
                    "mode": result.mode,
                    "status": result.status,
                    "exported_poses": result.exported_poses,
                    "output_root": str(result.output_root),
                    "message": result.message,
                },
                indent=2,
            )
        )

        if result.status != "ok" and not args.continue_on_error:
            raise RuntimeError(result.message)

    batch_dir = CROSS_MODEL_DIR / f"seqslam_full_eval_{args.run_label}" / "oxford" / "02_evo_batch"
    write_batch_summary(batch_dir, results)


if __name__ == "__main__":
    main()
