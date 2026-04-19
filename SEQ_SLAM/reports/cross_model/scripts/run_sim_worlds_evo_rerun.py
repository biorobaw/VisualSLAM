#!/usr/bin/env python3
"""Rerun SeqSLAM evo comparisons for the simulator world datasets.

This script converts the simulator pose CSV files into canonical TUM trajectories,
executes evo APE/RPE comparisons for the requested city/village pairs, exports
plots in a headless environment, updates the cross-model CSV summaries, and
writes a dated markdown report.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator

from convert_sim_poses_to_tum import convert as convert_sim_to_tum


SCRIPT_DIR = Path(__file__).resolve().parent
CROSS_MODEL_DIR = SCRIPT_DIR.parent
SEQ_SLAM_DIR = CROSS_MODEL_DIR.parent.parent
REPO_ROOT = SEQ_SLAM_DIR.parent

SANITY_CSV = CROSS_MODEL_DIR / "cross_model_sanity_results.csv"
BENCHMARK_CSV = CROSS_MODEL_DIR / "cross_model_benchmark_results.csv"

DATE_STR = date.today().isoformat()
MODEL_ID = "seq_slam"
OWNER = "SEQ_SLAM lane"
TRAJECTORY_FORMAT = "TUM"
ALIGNMENT = "SE3"
SYNC_TOLERANCE = "NA"
FPS = 10.0


@dataclass(frozen=True)
class EvalPair:
    sequence_id: str
    world: str
    gt_csv: Path
    est_csv: Path
    gt_tum_name: str
    est_tum_name: str
    result_kind: str
    eval_mode: str
    protocol_label: str
    notes: str


@dataclass
class EvalResult:
    pair: EvalPair
    pair_dir: Path
    gt_tum: Path
    est_tum: Path
    gt_pose_count: int
    est_pose_count: int
    gt_sha1: str
    est_sha1: str
    csvs_identical: bool
    ate_rmse: float
    rpe_trans_rmse: float
    rpe_rot_rmse: float


PAIR_DEFS = [
    EvalPair(
        sequence_id="city_night_vs_city_night",
        world="city",
        gt_csv=SEQ_SLAM_DIR / "datasets/city/city_night/poses.csv",
        est_csv=SEQ_SLAM_DIR / "datasets/city/city_night/poses.csv",
        gt_tum_name="seqslam_city_night_gt.tum.txt",
        est_tum_name="seqslam_city_night_est.tum.txt",
        result_kind="sanity",
        eval_mode="sanity_selfcheck",
        protocol_label="seqslam_sim_worlds_city_night_selfcheck_v1",
        notes="Night vs night self-check on refreshed city dataset to confirm the TUM + evo lane still runs cleanly.",
    ),
    EvalPair(
        sequence_id="city_summer_vs_city_night",
        world="city",
        gt_csv=SEQ_SLAM_DIR / "datasets/city/city_summer/poses.csv",
        est_csv=SEQ_SLAM_DIR / "datasets/city/city_night/poses.csv",
        gt_tum_name="seqslam_city_summer_gt.tum.txt",
        est_tum_name="seqslam_city_night_est.tum.txt",
        result_kind="benchmark",
        eval_mode="condition_shift_summer_vs_night",
        protocol_label="seqslam_sim_worlds_city_summer_vs_night_v1",
        notes="City summer vs city night using refreshed simulator datasets; current pose CSVs are byte-identical so zero geometry error is expected from evo.",
    ),
    EvalPair(
        sequence_id="village_winter_vs_village_winter",
        world="village",
        gt_csv=SEQ_SLAM_DIR / "datasets/village/village_winter/poses.csv",
        est_csv=SEQ_SLAM_DIR / "datasets/village/village_winter/poses.csv",
        gt_tum_name="seqslam_village_winter_gt.tum.txt",
        est_tum_name="seqslam_village_winter_est.tum.txt",
        result_kind="sanity",
        eval_mode="sanity_selfcheck",
        protocol_label="seqslam_sim_worlds_village_winter_selfcheck_v1",
        notes="Winter vs winter self-check on refreshed village dataset to confirm the TUM + evo lane still runs cleanly.",
    ),
    EvalPair(
        sequence_id="village_summer_vs_village_winter",
        world="village",
        gt_csv=SEQ_SLAM_DIR / "datasets/village/village_summer/poses.csv",
        est_csv=SEQ_SLAM_DIR / "datasets/village/village_winter/poses.csv",
        gt_tum_name="seqslam_village_summer_gt.tum.txt",
        est_tum_name="seqslam_village_winter_est.tum.txt",
        result_kind="benchmark",
        eval_mode="condition_shift_summer_vs_winter",
        protocol_label="seqslam_sim_worlds_village_summer_vs_winter_v1",
        notes="Village summer vs village winter using refreshed simulator datasets; current pose CSVs are byte-identical so zero geometry error is expected from evo.",
    ),
]


def sha1sum(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as fh:
        while chunk := fh.read(8192):
            digest.update(chunk)
    return digest.hexdigest()


def parse_rmse(stdout: str) -> float:
    match = re.search(r"^\s*rmse\s+([0-9.eE+-]+)\s*$", stdout, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Unable to parse rmse from evo output:\n{stdout}")
    return float(match.group(1))


def run_evo(
    command: list[str],
    output_txt: Path,
    env: dict[str, str],
) -> float:
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
    output_txt.write_text(combined)
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{combined}")
    return parse_rmse(completed.stdout)


@contextmanager
def headless_evo_env() -> Iterator[dict[str, str]]:
    settings_src = Path.home() / ".evo" / "settings.json"
    with tempfile.TemporaryDirectory(prefix="seqslam_evo_home_") as temp_home:
        evo_dir = Path(temp_home) / ".evo"
        evo_dir.mkdir(parents=True, exist_ok=True)

        if settings_src.exists():
            settings = json.loads(settings_src.read_text())
        else:
            settings = {}
        settings["plot_backend"] = "Agg"

        (evo_dir / "settings.json").write_text(json.dumps(settings, indent=4))

        env = os.environ.copy()
        env["HOME"] = temp_home
        yield env


def upsert_csv_row(csv_path: Path, row: dict[str, str]) -> None:
    with csv_path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError(f"Missing CSV header in {csv_path}")
        rows = list(reader)

    row_key = (row["date"], row["sequence_id"], row["protocol_label"])
    replaced = False
    for index, existing in enumerate(rows):
        existing_key = (existing["date"], existing["sequence_id"], existing["protocol_label"])
        if existing_key == row_key:
            rows[index] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)

    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_report(results: list[EvalResult], report_path: Path) -> None:
    lines = [
        "# SeqSLAM Sim Worlds Evo Rerun",
        "",
        f"Date: {DATE_STR}",
        "",
        "## Summary",
        "",
        "- Re-ran the SeqSLAM evo lane on the current simulator datasets using canonical TUM trajectories.",
        "- City summer/night pose CSVs are byte-identical, so the cross-condition city geometry metrics collapse to zero.",
        "- Village summer/winter pose CSVs are byte-identical, so the cross-condition village geometry metrics collapse to zero.",
        "- This confirms the TUM conversion + evo tooling still works, but the current simulator pose tracks do not create a non-trivial geometry benchmark.",
        "",
        "## Results",
        "",
        "| World | Sequence | Kind | GT poses | EST poses | CSV identical | ATE RMSE | RPE trans RMSE | RPE rot RMSE | Artifacts |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]

    for result in results:
        lines.append(
            "| {world} | {sequence_id} | {kind} | {gt_count} | {est_count} | {identical} | {ate:.6f} | {rpe_trans:.6f} | {rpe_rot:.6f} | `{artifacts}` |".format(
                world=result.pair.world,
                sequence_id=result.pair.sequence_id,
                kind=result.pair.result_kind,
                gt_count=result.gt_pose_count,
                est_count=result.est_pose_count,
                identical="yes" if result.csvs_identical else "no",
                ate=result.ate_rmse,
                rpe_trans=result.rpe_trans_rmse,
                rpe_rot=result.rpe_rot_rmse,
                artifacts=result.pair_dir.relative_to(REPO_ROOT),
            )
        )

    lines.extend(
        [
            "",
            "## Pose Hashes",
            "",
            "| Sequence | GT SHA1 | EST SHA1 |",
            "| --- | --- | --- |",
        ]
    )

    for result in results:
        lines.append(
            f"| {result.pair.sequence_id} | `{result.gt_sha1}` | `{result.est_sha1}` |"
        )

    lines.extend(
        [
            "",
            "## Commands",
            "",
            "- `evo_ape tum <gt> <est> -a -r full --save_results ... --save_plot ... --plot_mode xyz`",
            "- `evo_rpe tum <gt> <est> -a -r trans_part --save_results ... --save_plot ... --plot_mode xyz`",
            "- `evo_rpe tum <gt> <est> -a -r angle_deg --save_results ... --save_plot ... --plot_mode xyz`",
            "",
        ]
    )

    report_path.write_text("\n".join(lines))


def main() -> None:
    results: list[EvalResult] = []

    with headless_evo_env() as evo_env:
        for pair in PAIR_DEFS:
            pair_dir = CROSS_MODEL_DIR / "pilot" / MODEL_ID / pair.sequence_id
            inputs_dir = pair_dir / "inputs"
            outputs_dir = pair_dir / "outputs"
            inputs_dir.mkdir(parents=True, exist_ok=True)
            outputs_dir.mkdir(parents=True, exist_ok=True)

            gt_tum = inputs_dir / pair.gt_tum_name
            est_tum = inputs_dir / pair.est_tum_name

            gt_pose_count = convert_sim_to_tum(pair.gt_csv, gt_tum, FPS, False)
            est_pose_count = convert_sim_to_tum(pair.est_csv, est_tum, FPS, False)

            ate_rmse = run_evo(
                [
                    "evo_ape",
                    "tum",
                    str(gt_tum),
                    str(est_tum),
                    "-a",
                    "-r",
                    "full",
                    "--save_results",
                    str(outputs_dir / "ape_se3.zip"),
                    "--save_plot",
                    str(outputs_dir / "ape_se3.pdf"),
                    "--plot_mode",
                    "xyz",
                    "--no_warnings",
                ],
                outputs_dir / "ape_se3.txt",
                evo_env,
            )

            rpe_trans_rmse = run_evo(
                [
                    "evo_rpe",
                    "tum",
                    str(gt_tum),
                    str(est_tum),
                    "-a",
                    "-r",
                    "trans_part",
                    "--save_results",
                    str(outputs_dir / "rpe_trans.zip"),
                    "--save_plot",
                    str(outputs_dir / "rpe_trans.pdf"),
                    "--plot_mode",
                    "xyz",
                    "--no_warnings",
                ],
                outputs_dir / "rpe_trans.txt",
                evo_env,
            )

            rpe_rot_rmse = run_evo(
                [
                    "evo_rpe",
                    "tum",
                    str(gt_tum),
                    str(est_tum),
                    "-a",
                    "-r",
                    "angle_deg",
                    "--save_results",
                    str(outputs_dir / "rpe_rot.zip"),
                    "--save_plot",
                    str(outputs_dir / "rpe_rot.pdf"),
                    "--plot_mode",
                    "xyz",
                    "--no_warnings",
                ],
                outputs_dir / "rpe_rot.txt",
                evo_env,
            )

            result = EvalResult(
                pair=pair,
                pair_dir=pair_dir,
                gt_tum=gt_tum,
                est_tum=est_tum,
                gt_pose_count=gt_pose_count,
                est_pose_count=est_pose_count,
                gt_sha1=sha1sum(pair.gt_csv),
                est_sha1=sha1sum(pair.est_csv),
                csvs_identical=pair.gt_csv.read_bytes() == pair.est_csv.read_bytes(),
                ate_rmse=ate_rmse,
                rpe_trans_rmse=rpe_trans_rmse,
                rpe_rot_rmse=rpe_rot_rmse,
            )
            results.append(result)

    for result in results:
        row = {
            "date": DATE_STR,
            "sequence_id": result.pair.sequence_id,
            "model_id": MODEL_ID,
            "owner": OWNER,
            "protocol_label": result.pair.protocol_label,
            "eval_mode": result.pair.eval_mode,
            "trajectory_format": TRAJECTORY_FORMAT,
            "valid_input": "True",
            "ate_rmse": f"{result.ate_rmse:.6f}",
            "rpe_trans_rmse": f"{result.rpe_trans_rmse:.6f}",
            "rpe_rot_rmse": f"{result.rpe_rot_rmse:.6f}",
            "num_poses": str(min(result.gt_pose_count, result.est_pose_count)),
            "alignment": ALIGNMENT,
            "sync_tolerance_sec": SYNC_TOLERANCE,
            "notes": result.pair.notes,
        }
        target_csv = SANITY_CSV if result.pair.result_kind == "sanity" else BENCHMARK_CSV
        upsert_csv_row(target_csv, row)

    report_path = CROSS_MODEL_DIR / f"seqslam_sim_worlds_evo_rerun_{DATE_STR}.md"
    render_report(results, report_path)

    print(f"Completed {len(results)} evo comparisons.")
    print(f"Report: {report_path}")
    for result in results:
        print(
            f"{result.pair.sequence_id}: "
            f"ATE={result.ate_rmse:.6f}, "
            f"RPE(trans)={result.rpe_trans_rmse:.6f}, "
            f"RPE(rot)={result.rpe_rot_rmse:.6f}"
        )


if __name__ == "__main__":
    main()
