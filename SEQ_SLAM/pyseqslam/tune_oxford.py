"""
Auto-tune SeqSLAM parameters on Oxford RobotCar sequence pairs.

This script:
1) Builds (or loads) one contrast-enhanced difference matrix DD for a chosen
   reference/query pair.
2) Sweeps matching parameters (ds, velocity range, Rwindow).
3) Sweeps match threshold over each raw matching result.
4) Ranks configurations and saves a CSV summary + best-match plot.
"""

import argparse
import csv
import glob
import os
import time
from copy import deepcopy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from parameters import defaultParameters
from seqslam import SeqSLAM
from utils import AttributeDict


def _parse_int_list(value):
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def _parse_float_list(value):
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def _parse_velocity_ranges(value):
    ranges = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" not in token:
            raise ValueError(f"Invalid velocity range '{token}', expected form vmin-vmax")
        vmin_text, vmax_text = token.split("-", 1)
        vmin = float(vmin_text.strip())
        vmax = float(vmax_text.strip())
        if vmin > vmax:
            raise ValueError(f"Invalid range '{token}': vmin > vmax")
        ranges.append((vmin, vmax))
    return ranges


def _load_timestamps(image_path):
    all_images = sorted(glob.glob(f"{image_path}/*.png"))
    timestamps = [int(os.path.basename(img).replace(".png", "")) for img in all_images]
    return all_images, timestamps


def _split_match_indices(matches, threshold=0.9, min_match_index=1):
    match_idx = np.asarray(matches[:, 0], dtype=float).copy()
    quality = np.asarray(matches[:, 1], dtype=float)

    finite = np.isfinite(match_idx) & np.isfinite(quality)
    strong_enough = quality <= threshold
    plausible_index = match_idx >= min_match_index

    valid_mask = finite & strong_enough & plausible_index
    invalid_mask = ~valid_mask
    return match_idx, quality, valid_mask, invalid_mask


def _compute_composite_score(valid_ratio, corr, norm_mae, weights):
    corr_pos = max(0.0, float(corr))
    mae_score = 0.0 if not np.isfinite(norm_mae) else max(0.0, 1.0 - min(1.0, float(norm_mae)))

    score = (
        weights["valid"] * float(valid_ratio)
        + weights["corr"] * corr_pos
        + weights["mae"] * mae_score
    )
    return score, corr_pos, mae_score


def _evaluate_matches(matches, n_ref, n_query, threshold):
    match_idx, quality, valid_mask, invalid_mask = _split_match_indices(matches, threshold=threshold)

    valid_count = int(np.sum(valid_mask))
    invalid_count = int(np.sum(invalid_mask))
    valid_ratio = valid_count / float(n_query) if n_query > 0 else 0.0

    x = np.arange(n_query, dtype=float)
    expected = x * (max(1, n_ref - 1) / float(max(1, n_query - 1)))

    if valid_count > 0:
        abs_err = np.abs(match_idx[valid_mask] - expected[valid_mask])
        mae = float(np.mean(abs_err))
        norm_mae = mae / float(max(1, n_ref - 1))
    else:
        mae = float("inf")
        norm_mae = float("inf")

    if valid_count >= 3:
        corr = float(np.corrcoef(x[valid_mask], match_idx[valid_mask])[0, 1])
        if np.isnan(corr):
            corr = 0.0
    else:
        corr = 0.0

    return {
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "valid_ratio": valid_ratio,
        "mae": mae,
        "norm_mae": norm_mae,
        "corr": corr,
        "nan_quality_count": int(np.sum(~np.isfinite(quality))),
    }


def _evaluate_core_consistency(matches, n_ref, n_query, ds, threshold=None, min_match_index=1):
    match_idx = np.asarray(matches[:, 0], dtype=float).copy()
    quality = np.asarray(matches[:, 1], dtype=float)

    half_ds = int(max(0, ds // 2))
    core_start = half_ds
    core_end = max(core_start, n_query - half_ds)

    core_mask = np.zeros(n_query, dtype=bool)
    if core_end > core_start:
        core_mask[core_start:core_end] = True

    finite = np.isfinite(match_idx) & np.isfinite(quality)
    plausible_index = match_idx >= min_match_index
    valid = finite & plausible_index
    if threshold is not None:
        valid = valid & (quality <= float(threshold))

    core_valid = core_mask & valid
    core_total = int(np.sum(core_mask))
    core_valid_count = int(np.sum(core_valid))
    core_valid_ratio = core_valid_count / float(core_total) if core_total > 0 else 0.0

    x = np.arange(n_query, dtype=float)
    expected = x * (max(1, n_ref - 1) / float(max(1, n_query - 1)))

    if core_valid_count > 0:
        abs_err = np.abs(match_idx[core_valid] - expected[core_valid])
        core_mae = float(np.mean(abs_err))
        core_norm_mae = core_mae / float(max(1, n_ref - 1))
    else:
        core_mae = float("inf")
        core_norm_mae = float("inf")

    if core_valid_count >= 3:
        core_corr = float(np.corrcoef(x[core_valid], match_idx[core_valid])[0, 1])
        if np.isnan(core_corr):
            core_corr = 0.0
    else:
        core_corr = 0.0

    return {
        "core_frame_start": core_start,
        "core_frame_end_exclusive": core_end,
        "core_total_count": core_total,
        "core_valid_count": core_valid_count,
        "core_valid_ratio": core_valid_ratio,
        "core_mae": core_mae,
        "core_norm_mae": core_norm_mae,
        "core_corr": core_corr,
    }


def _plot_matches(matches, threshold, save_path, title):
    m, _, valid_mask, invalid_mask = _split_match_indices(matches, threshold=threshold)
    x = np.arange(len(m))

    valid_count = int(np.sum(valid_mask))
    invalid_count = int(np.sum(invalid_mask))

    plt.figure(figsize=(11, 6))

    if valid_count > 0:
        plt.scatter(x[valid_mask], m[valid_mask], s=10, label="Valid matches")

    invalid_y = -0.03 * len(m)
    if invalid_count > 0:
        plt.scatter(
            x[invalid_mask],
            np.full(invalid_count, invalid_y),
            s=12,
            marker="x",
            color="tab:red",
            label="Invalid/filtered matches",
        )

    plt.plot([0, len(m)], [0, len(m)], "r--", alpha=0.3, label="Perfect diagonal")
    plt.ylim(bottom=invalid_y * 1.5)
    plt.xlabel("Second sequence frame")
    plt.ylabel("Matched first sequence frame")
    plt.title(title)
    plt.legend()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def _prepare_params(reference_run, query_run, use_cache=True, query_stride=1, auto_query_stride=False):
    params = defaultParameters()
    params.DO_RESIZE = 1

    reference_path = f"../datasets/oxford/{reference_run}/mono_left"
    query_path = f"../datasets/oxford/{query_run}/mono_left"

    ref_images, ref_timestamps = _load_timestamps(reference_path)
    qry_images, qry_timestamps = _load_timestamps(query_path)

    if len(ref_images) == 0 or len(qry_images) == 0:
        raise FileNotFoundError(
            "No Oxford .png images found for one or both runs. "
            "Check dataset paths and run ids."
        )

    effective_query_stride = max(1, int(query_stride))
    if auto_query_stride and len(qry_timestamps) > len(ref_timestamps):
        estimated = int(round(len(qry_timestamps) / float(len(ref_timestamps))))
        effective_query_stride = max(1, estimated)

    qry_timestamps = qry_timestamps[::effective_query_stride]

    ds1 = AttributeDict()
    ds1.name = "oxford_reference"
    ds1.imagePath = reference_path
    ds1.prefix = ""
    ds1.extension = ".png"
    ds1.suffix = ""
    ds1.imageSkip = 1
    ds1.imageIndices = ref_timestamps
    ds1.savePath = "results"
    ds1.saveFile = "oxford_reference"
    ds1.preprocessing = AttributeDict()
    ds1.preprocessing.save = 1
    ds1.preprocessing.load = 1 if use_cache else 0
    ds1.crop = []

    ds2 = deepcopy(ds1)
    ds2.name = "oxford_query"
    ds2.imagePath = query_path
    ds2.imageIndices = qry_timestamps
    ds2.saveFile = "oxford_query"
    ds2.preprocessing.load = 1 if (use_cache and effective_query_stride == 1) else 0

    params.dataset = [ds1, ds2]
    params.savePath = "results"

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


def _run_tuning(args):
    (
        params,
        reference_path,
        query_path,
        n_ref_images,
        n_qry_images_raw,
        n_qry_images_used,
        effective_query_stride,
    ) = _prepare_params(
        args.reference_run,
        args.query_run,
        use_cache=not args.no_cache,
        query_stride=args.query_stride,
        auto_query_stride=args.auto_query_stride,
    )

    result_dir = f"results/oxford/Oxford_{args.reference_run}_vs_{args.query_run}"
    os.makedirs(result_dir, exist_ok=True)

    print("=" * 72)
    print("SeqSLAM Oxford Auto-Tuning")
    print("=" * 72)
    print(f"Reference path: {reference_path}")
    print(f"Query path:     {query_path}")
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
            print("Cache loading failed due to legacy .mat structure, retrying with --no-cache semantics...")
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
    print(f"Total matcher runs: {total_match_runs} (each reused over thresholds)")

    rows = []
    run_counter = 0
    rank_weights = {
        "valid": float(args.weight_valid),
        "corr": float(args.weight_corr),
        "mae": float(args.weight_mae),
    }

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
                    f"[{run_counter}/{total_match_runs}] matching with "
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
        raise RuntimeError("No tuning results generated.")

    rows_sorted = sorted(
        rows,
        key=lambda row: (
            -row["rank_score"],
            -row["valid_ratio"],
            -row["corr"],
            row["norm_mae"] if np.isfinite(row["norm_mae"]) else 1e9,
        ),
    )
    best = rows_sorted[0]

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

    best_plot_path = os.path.join(result_dir, "oxford_tuning_best_matchings.png")
    _plot_matches(
        best_matches,
        threshold=float(best["threshold"]),
        save_path=best_plot_path,
        title=(
            "Best tuned matching "
            f"(ds={best['ds']}, v=({best['vmin']:.2f},{best['vmax']:.2f}), "
            f"Rwindow={best['Rwindow']}, thresh={best['threshold']:.2f}, "
            f"valid={best['valid_count']}/{n_query})"
        ),
    )

    print("\n" + "=" * 72)
    print("Tuning completed")
    print("=" * 72)
    print(f"CSV summary: {csv_path}")
    print(f"Best plot:   {best_plot_path}")
    print("Best config:")
    print(
        f"  ds={best['ds']}, vmin={best['vmin']:.2f}, vmax={best['vmax']:.2f}, "
        f"Rwindow={best['Rwindow']}, threshold={best['threshold']:.2f}"
    )
    print(
        f"  valid={best['valid_count']}/{n_query} "
        f"({100.0 * best['valid_ratio']:.2f}%), "
        f"invalid={best['invalid_count']}/{n_query}"
    )
    print(
        f"  core_valid={best['core_valid_count']}/{best['core_total_count']} "
        f"({100.0 * best['core_valid_ratio']:.2f}%), "
        f"core_window=[{best['core_frame_start']},{best['core_frame_end_exclusive']})"
    )
    print(
        f"  rank_score={best['rank_score']:.4f} "
        f"(weights: valid={rank_weights['valid']}, corr={rank_weights['corr']}, mae={rank_weights['mae']})"
    )
    if np.isfinite(best["norm_mae"]):
        print(
            f"  mae={best['mae']:.2f} frames, "
            f"normalized_mae={best['norm_mae']:.4f}, corr={best['corr']:.4f}"
        )
    if np.isfinite(best["core_norm_mae"]):
        print(
            f"  core_mae={best['core_mae']:.2f} frames, "
            f"core_normalized_mae={best['core_norm_mae']:.4f}, core_corr={best['core_corr']:.4f}"
        )


def main():
    parser = argparse.ArgumentParser(description="Auto-tune SeqSLAM Oxford matching parameters")
    parser.add_argument("--reference-run", default="2014-05-14-13-46-12")
    parser.add_argument("--query-run", default="2014-05-14-13-50-20")
    parser.add_argument("--ds-values", default="10,20,30,50")
    parser.add_argument("--rwindow-values", default="10,30,50")
    parser.add_argument("--velocity-ranges", default="0.8-1.2,0.5-1.5,0.3-2.0")
    parser.add_argument("--threshold-values", default="0.8,0.9,1.0")
    parser.add_argument("--query-stride", type=int, default=1, help="Use every Nth query frame")
    parser.add_argument(
        "--auto-query-stride",
        action="store_true",
        help="If query is longer than reference, auto-downsample query by length ratio",
    )
    parser.add_argument("--weight-valid", type=float, default=0.45)
    parser.add_argument("--weight-corr", type=float, default=0.40)
    parser.add_argument("--weight-mae", type=float, default=0.15)
    parser.add_argument(
        "--core-use-threshold",
        action="store_true",
        help="Apply threshold filtering to core consistency metrics (off by default).",
    )
    parser.add_argument("--no-cache", action="store_true", help="Force recomputing preprocessing/DD")

    args = parser.parse_args()
    _run_tuning(args)


if __name__ == "__main__":
    main()
