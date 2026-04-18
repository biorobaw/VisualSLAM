"""
Auto-tune SeqSLAM on simulator City/Village world datasets.

This is a separate evaluation phase from Oxford.
Evaluated pairs:
1) city summer    vs city summer
2) city summer    vs city night
3) village summer vs village summer
4) village summer vs village winter
"""

import argparse
import csv
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from parameters import defaultParameters
from seqslam import SeqSLAM
from tune_oxford import (
    _compute_composite_score,
    _evaluate_core_consistency,
    _evaluate_matches,
    _load_timestamps,
    _parse_float_list,
    _parse_int_list,
    _parse_velocity_ranges,
    _plot_matches,
)
from utils import AttributeDict


@dataclass
class TuningPair:
    dataset_group: str
    reference_run: str
    query_run: str


def _sanitize_tag(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())


def _load_pairs_from_csv(csv_path):
    pairs = []
    with open(csv_path, newline="") as fp:
        reader = csv.DictReader(fp)
        required = {"dataset_group", "reference_run", "query_run"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                f"Pair CSV must include columns: {sorted(required)}; found: {reader.fieldnames}"
            )

        for row in reader:
            dataset_group = (row.get("dataset_group") or "").strip()
            reference_run = (row.get("reference_run") or "").strip()
            query_run = (row.get("query_run") or "").strip()

            if not dataset_group and not reference_run and not query_run:
                continue
            if not dataset_group or not reference_run or not query_run:
                raise ValueError(f"Invalid pair row with missing values: {row}")

            pairs.append(TuningPair(dataset_group, reference_run, query_run))

    if not pairs:
        raise ValueError(f"No valid pairs found in CSV: {csv_path}")
    return pairs


def _prepare_params_generic(
    dataset_group,
    reference_run,
    query_run,
    camera_subdir="mono_front",
    use_cache=False,
    query_stride=1,
    auto_query_stride=True,
):
    params = defaultParameters()
    params.DO_RESIZE = 1

    reference_path = f"../datasets/{dataset_group}/{reference_run}/{camera_subdir}"
    query_path = f"../datasets/{dataset_group}/{query_run}/{camera_subdir}"

    ref_images, ref_timestamps = _load_timestamps(reference_path)
    qry_images, qry_timestamps = _load_timestamps(query_path)

    if len(ref_images) == 0 or len(qry_images) == 0:
        raise FileNotFoundError(
            f"No .png images found for one or both runs: {reference_path} | {query_path}"
        )

    effective_query_stride = max(1, int(query_stride))
    if auto_query_stride and len(qry_timestamps) > len(ref_timestamps):
        estimated = int(round(len(qry_timestamps) / float(len(ref_timestamps))))
        effective_query_stride = max(1, estimated)

    qry_timestamps = qry_timestamps[::effective_query_stride]

    safe_ref = reference_run.replace("/", "_")
    safe_qry = query_run.replace("/", "_")

    cache_save_path = "results/sim_worlds_cache"
    os.makedirs(cache_save_path, exist_ok=True)

    ds1 = AttributeDict()
    ds1.name = f"{dataset_group}_reference"
    ds1.imagePath = reference_path
    ds1.prefix = ""
    ds1.extension = ".png"
    ds1.suffix = ""
    ds1.imageSkip = 1
    ds1.imageIndices = ref_timestamps
    ds1.savePath = cache_save_path
    ds1.saveFile = f"{dataset_group}_{safe_ref}_reference"
    ds1.preprocessing = AttributeDict()
    ds1.preprocessing.save = 1
    ds1.preprocessing.load = 1 if use_cache else 0
    ds1.crop = []

    ds2 = deepcopy(ds1)
    ds2.name = f"{dataset_group}_query"
    ds2.imagePath = query_path
    ds2.imageIndices = qry_timestamps
    ds2.saveFile = f"{dataset_group}_{safe_qry}_query"
    ds2.preprocessing.load = 1 if (use_cache and effective_query_stride == 1) else 0

    params.dataset = [ds1, ds2]
    params.savePath = cache_save_path

    params.differenceMatrix.load = 1 if (use_cache and effective_query_stride == 1) else 0
    params.contrastEnhanced.load = 1 if (use_cache and effective_query_stride == 1) else 0
    params.matching.load = 0

    return (
        params,
        reference_path,
        query_path,
        len(ref_images),
        len(qry_images),
        len(qry_timestamps),
        effective_query_stride,
    )


def _run_pair(pair, args):
    (
        params,
        reference_path,
        query_path,
        n_ref_images,
        n_qry_images_raw,
        n_qry_images_used,
        effective_query_stride,
    ) = _prepare_params_generic(
        pair.dataset_group,
        pair.reference_run,
        pair.query_run,
        camera_subdir=args.camera_subdir,
        use_cache=not args.no_cache,
        query_stride=args.query_stride,
        auto_query_stride=args.auto_query_stride,
    )

    result_suffix = f"_{_sanitize_tag(args.result_tag)}" if args.result_tag else ""
    result_dir = (
        f"results/sim_worlds/{pair.dataset_group}/"
        f"{pair.dataset_group}_{pair.reference_run}_vs_{pair.query_run}{result_suffix}"
    )
    os.makedirs(result_dir, exist_ok=True)

    print("=" * 72)
    print(f"SeqSLAM Sim-World Auto-Tuning: {pair.dataset_group}")
    print("=" * 72)
    print(f"Reference path: {reference_path}")
    print(f"Query path:     {query_path}")
    print(f"Camera path:    {args.camera_subdir}")
    print(f"Reference frames found: {n_ref_images}")
    print(f"Query frames found (raw):  {n_qry_images_raw}")
    print(f"Query frames used (stride={effective_query_stride}): {n_qry_images_used}")

    params.DO_FIND_MATCHES = 0
    ss = SeqSLAM(params)

    t0 = time.time()
    try:
        results = ss.run()
    except AttributeError as exc:
        if "results_preprocessing" in str(exc) and not args.no_cache:
            print("Cache loading failed; retrying with cache disabled for this pair...")
            params.dataset[0].preprocessing.load = 0
            params.dataset[1].preprocessing.load = 0
            params.differenceMatrix.load = 0
            params.contrastEnhanced.load = 0
            ss = SeqSLAM(params)
            results = ss.run()
        else:
            raise
    t1 = time.time()

    base_dd = results.DD
    n_ref, n_query = base_dd.shape
    print(f"Built/loaded DD matrix in {t1 - t0:.2f}s with shape ({n_ref}, {n_query})")

    ds_values = _parse_int_list(args.ds_values)
    rwindow_values = _parse_int_list(args.rwindow_values)
    threshold_values = _parse_float_list(args.threshold_values)
    velocity_ranges = _parse_velocity_ranges(args.velocity_ranges)

    total_match_runs = len(ds_values) * len(rwindow_values) * len(velocity_ranges)
    rank_weights = {
        "valid": float(args.weight_valid),
        "corr": float(args.weight_corr),
        "mae": float(args.weight_mae),
    }

    rows = []
    run_counter = 0

    for ds in ds_values:
        even_ds = ds + (ds % 2)
        for rwindow in rwindow_values:
            for vmin, vmax in velocity_ranges:
                run_counter += 1
                ss.params.matching.ds = even_ds
                ss.params.matching.Rwindow = int(rwindow)
                ss.params.matching.vmin = float(vmin)
                ss.params.matching.vmax = float(vmax)

                print(
                    f"[{run_counter}/{total_match_runs}] {pair.dataset_group} matching with "
                    f"ds={even_ds}, v=({vmin:.2f},{vmax:.2f}), Rwindow={rwindow}"
                )

                match_start = time.time()
                matches = ss.getMatches(base_dd)
                match_elapsed = time.time() - match_start

                for threshold in threshold_values:
                    metrics = _evaluate_matches(matches, n_ref, n_query, threshold)
                    core_metrics = _evaluate_core_consistency(
                        matches,
                        n_ref,
                        n_query,
                        ds=even_ds,
                        threshold=(threshold if args.core_use_threshold else None),
                    )
                    composite, corr_pos, mae_score = _compute_composite_score(
                        metrics["valid_ratio"],
                        metrics["corr"],
                        metrics["norm_mae"],
                        rank_weights,
                    )
                    rows.append(
                        {
                            "ds": even_ds,
                            "vmin": vmin,
                            "vmax": vmax,
                            "Rwindow": int(rwindow),
                            "threshold": threshold,
                            "match_runtime_sec": round(match_elapsed, 4),
                            "rank_score": composite,
                            "score_valid": metrics["valid_ratio"],
                            "score_corr": corr_pos,
                            "score_mae": mae_score,
                            **metrics,
                            **core_metrics,
                        }
                    )

    if not rows:
        raise RuntimeError("No tuning rows generated.")

    rows_sorted = sorted(
        rows,
        key=lambda row: (
            -row["rank_score"],
            -row["valid_ratio"],
            -row["corr"],
            row["norm_mae"] if np.isfinite(row["norm_mae"]) else 1e9,
        ),
    )

    gated_rows = [
        row
        for row in rows_sorted
        if (row["valid_ratio"] >= float(args.min_valid_ratio))
        and (row["valid_count"] >= int(args.min_valid_count))
    ]

    best = gated_rows[0] if gated_rows else rows_sorted[0]
    selected_with_gate = bool(gated_rows)

    csv_path = os.path.join(result_dir, "tuning_summary.csv")
    with open(csv_path, "w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "ds",
                "vmin",
                "vmax",
                "Rwindow",
                "threshold",
                "match_runtime_sec",
                "rank_score",
                "score_valid",
                "score_corr",
                "score_mae",
                "valid_count",
                "invalid_count",
                "valid_ratio",
                "mae",
                "norm_mae",
                "corr",
                "nan_quality_count",
                "core_frame_start",
                "core_frame_end_exclusive",
                "core_total_count",
                "core_valid_count",
                "core_valid_ratio",
                "core_mae",
                "core_norm_mae",
                "core_corr",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_sorted)

    ss.params.matching.ds = int(best["ds"])
    ss.params.matching.Rwindow = int(best["Rwindow"])
    ss.params.matching.vmin = float(best["vmin"])
    ss.params.matching.vmax = float(best["vmax"])
    best_matches = ss.getMatches(base_dd)

    best_plot_path = os.path.join(result_dir, "sim_worlds_tuning_best_matchings.png")
    _plot_matches(
        best_matches,
        threshold=float(best["threshold"]),
        save_path=best_plot_path,
        title=(
            f"Best tuned matching ({pair.dataset_group}) "
            f"(ds={best['ds']}, v=({best['vmin']:.2f},{best['vmax']:.2f}), "
            f"Rwindow={best['Rwindow']}, thresh={best['threshold']:.2f}, "
            f"valid={best['valid_count']}/{n_query})"
        ),
        n_ref=n_ref,
    )

    tuning_pass = bool(best["valid_count"] > 0 and np.isfinite(best["rank_score"]))

    return {
        "dataset_group": pair.dataset_group,
        "reference_run": pair.reference_run,
        "query_run": pair.query_run,
        "camera_subdir": args.camera_subdir,
        "protocol": args.protocol_label,
        "best_ds": int(best["ds"]),
        "best_vmin": float(best["vmin"]),
        "best_vmax": float(best["vmax"]),
        "best_rwindow": int(best["Rwindow"]),
        "best_threshold": float(best["threshold"]),
        "valid_count": int(best["valid_count"]),
        "invalid_count": int(best["invalid_count"]),
        "valid_ratio": float(best["valid_ratio"]),
        "core_valid_ratio": float(best["core_valid_ratio"]),
        "corr": float(best["corr"]),
        "core_corr": float(best["core_corr"]),
        "norm_mae": float(best["norm_mae"]),
        "core_norm_mae": float(best["core_norm_mae"]),
        "rank_score": float(best["rank_score"]),
        "selected_with_gate": selected_with_gate,
        "min_valid_ratio_gate": float(args.min_valid_ratio),
        "min_valid_count_gate": int(args.min_valid_count),
        "tuning_pass": tuning_pass,
        "result_dir": f"SEQ_SLAM/pyseqslam/{result_dir}",
        "tuning_summary_csv": f"SEQ_SLAM/pyseqslam/{result_dir}/tuning_summary.csv",
        "best_plot": f"SEQ_SLAM/pyseqslam/{result_dir}/sim_worlds_tuning_best_matchings.png",
    }


def _write_outputs(rows, report_dir, command_text):
    os.makedirs(report_dir, exist_ok=True)

    summary_csv = report_dir / "summary.csv"
    with open(summary_csv, "w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "dataset_group",
                "reference_run",
                "query_run",
                "camera_subdir",
                "protocol",
                "best_ds",
                "best_vmin",
                "best_vmax",
                "best_rwindow",
                "best_threshold",
                "valid_count",
                "invalid_count",
                "valid_ratio",
                "core_valid_ratio",
                "corr",
                "core_corr",
                "norm_mae",
                "core_norm_mae",
                "rank_score",
                "selected_with_gate",
                "min_valid_ratio_gate",
                "min_valid_count_gate",
                "tuning_pass",
                "result_dir",
                "tuning_summary_csv",
                "best_plot",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(1 for r in rows if r["tuning_pass"])
    total = len(rows)

    report_md = report_dir / "report.md"
    with open(report_md, "w") as fp:
        fp.write("# City/Village Simulator Tuning Report\n\n")
        fp.write("This is a separate evaluation track from Oxford.\n\n")
        fp.write(f"Protocol: **{rows[0]['protocol']}**\n\n")
        fp.write("## Evaluated comparisons\n")
        for r in rows:
            fp.write(
                f"- {r['dataset_group']}: {r['reference_run']} vs {r['query_run']} "
                f"(camera: {r['camera_subdir']})\n"
            )
        fp.write("\n")
        fp.write("## Command\n")
        fp.write("```bash\n")
        fp.write(command_text + "\n")
        fp.write("```\n\n")
        fp.write(f"## Outcome\n- Tunings passed: **{passed}/{total}**\n\n")
        fp.write("## Per-pair best tuning summary\n\n")
        fp.write("| Dataset | Reference | Query | Pass | Rank | Valid Ratio | Corr | Norm MAE | Best Params |\n")
        fp.write("|---|---|---|---:|---:|---:|---:|---:|---|\n")
        for r in rows:
            fp.write(
                f"| {r['dataset_group']} | {r['reference_run']} | {r['query_run']} | "
                f"{str(r['tuning_pass'])} | {r['rank_score']:.4f} | {r['valid_ratio']:.4f} | "
                f"{r['corr']:.4f} | {r['norm_mae']:.4f} | "
                f"ds={r['best_ds']}, v=({r['best_vmin']:.2f},{r['best_vmax']:.2f}), "
                f"R={r['best_rwindow']}, th={r['best_threshold']:.2f}, "
                f"gate={str(r['selected_with_gate'])} |\n"
            )
        fp.write("\n## Artifact index\n")
        for r in rows:
            fp.write(f"- {r['tuning_summary_csv']}\n")
            fp.write(f"- {r['best_plot']}\n")

    return summary_csv, report_md


def main():
    parser = argparse.ArgumentParser(description="Auto-tune SeqSLAM on City/Village sim-world pairs")
    parser.add_argument(
        "--pairs-csv",
        default="",
        help=(
            "Optional CSV path with columns dataset_group,reference_run,query_run. "
            "If omitted, the built-in baseline 4 pairs are used."
        ),
    )
    parser.add_argument(
        "--protocol-label",
        default="city_village_worlds_auto_stride",
        help="Protocol label written into summary/report outputs.",
    )
    parser.add_argument(
        "--report-subdir",
        default="CityVillage_worlds",
        help="Subdirectory under SEQ_SLAM/reports/sim_worlds for generated summary/report files.",
    )
    parser.add_argument(
        "--camera-subdir",
        default="mono_front",
        help="Camera subdirectory to use from each sim-world run.",
    )
    parser.add_argument(
        "--result-tag",
        default="",
        help="Optional suffix appended to each per-pair result directory.",
    )
    parser.add_argument(
        "--min-valid-ratio",
        type=float,
        default=0.0,
        help="Minimum valid_ratio required when selecting the best row.",
    )
    parser.add_argument(
        "--min-valid-count",
        type=int,
        default=0,
        help="Minimum valid_count required when selecting the best row.",
    )
    parser.add_argument("--ds-values", default="10,20,30,50")
    parser.add_argument("--rwindow-values", default="10,30,50")
    parser.add_argument("--velocity-ranges", default="0.8-1.2,0.5-1.5,0.3-2.0")
    parser.add_argument("--threshold-values", default="0.8,0.9,1.0")
    parser.add_argument("--query-stride", type=int, default=1)
    parser.add_argument("--auto-query-stride", action="store_true", default=True)
    parser.add_argument("--weight-valid", type=float, default=0.45)
    parser.add_argument("--weight-corr", type=float, default=0.40)
    parser.add_argument("--weight-mae", type=float, default=0.15)
    parser.add_argument("--core-use-threshold", action="store_true")
    parser.add_argument("--no-cache", action="store_true", default=True)
    args = parser.parse_args()

    if args.pairs_csv:
        pairs = _load_pairs_from_csv(args.pairs_csv)
    else:
        pairs = [
            TuningPair("city", "city_summer", "city_summer"),
            TuningPair("city", "city_summer", "city_night"),
            TuningPair("village", "village_summer", "village_summer"),
            TuningPair("village", "village_summer", "village_winter"),
        ]

    all_rows = []
    for idx, pair in enumerate(pairs, start=1):
        print("\n" + "#" * 72)
        print(f"[{idx}/{len(pairs)}] Running pair: {pair.dataset_group} {pair.reference_run} vs {pair.query_run}")
        print("#" * 72)
        row = _run_pair(pair, args)
        all_rows.append(row)

    repo_root = Path(__file__).resolve().parents[2]
    report_dir = repo_root / "SEQ_SLAM/reports/sim_worlds" / args.report_subdir

    cmd = f"{repo_root}/.venv/bin/python -u tune_sim_worlds.py {' '.join(sys.argv[1:])}".strip()
    summary_csv, report_md = _write_outputs(all_rows, report_dir, cmd)

    print("\n" + "=" * 72)
    print("City/Village simulator tuning completed")
    print("=" * 72)
    print(f"Summary CSV: {summary_csv}")
    print(f"Report MD:   {report_md}")


if __name__ == "__main__":
    main()
