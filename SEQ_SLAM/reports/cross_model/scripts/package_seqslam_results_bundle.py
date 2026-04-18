#!/usr/bin/env python3
"""Collect SeqSLAM tuning artifacts and evo artifacts into one bundle folder."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package SeqSLAM and evo artifacts into one folder")
    parser.add_argument("--summary-csv", required=True)
    parser.add_argument("--seqslam-report", required=True)
    parser.add_argument("--requested-pairs-csv", required=True)
    parser.add_argument("--evo-report", required=True)
    parser.add_argument("--benchmark-csv", required=True)
    parser.add_argument("--sanity-csv", required=True)
    parser.add_argument(
        "--evo-results-root",
        default="SEQ_SLAM/reports/cross_model/pilot/seq_slam",
        help="Repo-relative root directory that holds per-pair evo artifacts.",
    )
    parser.add_argument("--bundle-dir", required=True)
    return parser.parse_args()


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fp:
        reader = csv.DictReader(fp)
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError(f"Missing header in {path}")
        return fieldnames, list(reader)


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def sequence_id(row: dict[str, str]) -> str:
    return f"{row['reference_run']}_vs_{row['query_run']}"


def write_readme(
    path: Path,
    protocol: str,
    summary_rows: list[dict[str, str]],
    benchmark_rows: list[dict[str, str]],
    sanity_rows: list[dict[str, str]],
) -> None:
    lines = [
        "# SeqSLAM HQ Bundle",
        "",
        f"Protocol: `{protocol}`",
        "",
        "## Layout",
        "",
        "- `01_seqslam_batch/`: top-level SeqSLAM report, summary table, and requested pair list.",
        "- `02_evo_batch/`: top-level evo report plus filtered sanity and benchmark CSV snapshots for this protocol.",
        "- `03_pairs/<pair>/01_seqslam/`: per-pair SeqSLAM tuning artifacts.",
        "- `03_pairs/<pair>/02_evo/`: per-pair TUM inputs, matched frame export, evo plots, text outputs, and result archives.",
        "",
        "## SeqSLAM Pairs",
        "",
        "| Pair | Rank | Valid Ratio | Corr | Best Params |",
        "| --- | ---: | ---: | ---: | --- |",
    ]

    for row in summary_rows:
        lines.append(
            f"| {sequence_id(row)} | {float(row['rank_score']):.4f} | {float(row['valid_ratio']):.4f} | "
            f"{float(row['corr']):.4f} | ds={row['best_ds']}, v=({float(row['best_vmin']):.2f},{float(row['best_vmax']):.2f}), "
            f"R={row['best_rwindow']}, th={float(row['best_threshold']):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Evo Snapshot",
            "",
            "| Pair | Mode | APE | RPE Trans | RPE Rot | Eval Poses |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )

    for row in benchmark_rows + sanity_rows:
        lines.append(
            f"| {row['sequence_id']} | {row['eval_mode']} | {float(row['ate_rmse']):.6f} | "
            f"{float(row['rpe_trans_rmse']):.6f} | {float(row['rpe_rot_rmse']):.6f} | {row['num_poses']} |"
        )

    path.write_text("\n".join(lines))


def main() -> None:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    seqslam_report = Path(args.seqslam_report).resolve()
    requested_pairs_csv = Path(args.requested_pairs_csv).resolve()
    evo_report = Path(args.evo_report).resolve()
    benchmark_csv = Path(args.benchmark_csv).resolve()
    sanity_csv = Path(args.sanity_csv).resolve()
    evo_results_root = (REPO_ROOT / args.evo_results_root).resolve()
    bundle_dir = Path(args.bundle_dir).resolve()

    summary_fields, summary_rows = load_rows(summary_csv)
    if not summary_rows:
        raise RuntimeError("No summary rows found")

    protocol = summary_rows[0]["protocol"]
    protocol_label = f"seqslam_match_export_{protocol}"

    benchmark_fields, benchmark_rows_all = load_rows(benchmark_csv)
    sanity_fields, sanity_rows_all = load_rows(sanity_csv)
    benchmark_rows = [row for row in benchmark_rows_all if row["protocol_label"] == protocol_label]
    sanity_rows = [row for row in sanity_rows_all if row["protocol_label"] == protocol_label]

    seqslam_batch_dir = bundle_dir / "01_seqslam_batch"
    evo_batch_dir = bundle_dir / "02_evo_batch"
    pairs_dir = bundle_dir / "03_pairs"

    seqslam_batch_dir.mkdir(parents=True, exist_ok=True)
    evo_batch_dir.mkdir(parents=True, exist_ok=True)
    pairs_dir.mkdir(parents=True, exist_ok=True)

    copy_file(seqslam_report, seqslam_batch_dir / "report.md")
    copy_file(summary_csv, seqslam_batch_dir / "summary.csv")
    copy_file(requested_pairs_csv, seqslam_batch_dir / "requested_pairs.csv")

    copy_file(evo_report, evo_batch_dir / "report.md")
    write_rows(evo_batch_dir / "benchmark_rows.csv", benchmark_fields, benchmark_rows)
    write_rows(evo_batch_dir / "sanity_rows.csv", sanity_fields, sanity_rows)

    for row in summary_rows:
        pair = sequence_id(row)
        pair_dir = pairs_dir / pair
        pair_seqslam_dir = pair_dir / "01_seqslam"
        pair_evo_dir = pair_dir / "02_evo"

        seqslam_result_dir = (REPO_ROOT / row["result_dir"]).resolve()
        evo_result_dir = (evo_results_root / pair).resolve()

        copy_dir(seqslam_result_dir, pair_seqslam_dir)
        copy_dir(evo_result_dir, pair_evo_dir)

    write_readme(bundle_dir / "README.md", protocol, summary_rows, benchmark_rows, sanity_rows)
    print(bundle_dir)


if __name__ == "__main__":
    main()
