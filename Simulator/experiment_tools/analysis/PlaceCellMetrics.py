#!/usr/bin/env python3
"""
compute_vpc_metrics.py

Batch-compute Metrics 1–6 for Visual Place Cell networks across multiple K values.

All file paths are interpreted relative to the repository root:
    REPO_ROOT = Path.cwd().parents[2]

Example
-------
python compute_vpc_metrics.py \
  --pickle data/activations/activations_LM8.pkl \
  --env_id LM8 \
  --tau 0.20 \
  --aocc 14.80
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
REPO_ROOT = Path.cwd().parents[2]


# -----------------------------------------------------------------------------
# Metric helper functions
# -----------------------------------------------------------------------------
def _extract_A_positions(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Return activation matrix A (K x N), positions (N x 2), and list of pc_* columns."""
    pc_cols = [c for c in df.columns if str(c).startswith("pc_")]
    if len(pc_cols) == 0:
        raise ValueError("No pc_* columns found in DataFrame.")
    A = df[pc_cols].to_numpy(dtype=float).T  # shape: (K, N)
    positions = df[["x", "y"]].to_numpy(dtype=float)      # shape: (N, 2)
    return A, positions, pc_cols


def metric1_place_field_size(df: pd.DataFrame, A_OCC: float, tau: float) -> pd.DataFrame:
    """Metric 1: Place-field size per cell (m^2)."""
    A, positions, pc_cols = _extract_A_positions(df)
    K, N = A.shape
    a_pix = float(A_OCC) / float(N)

    per_cell_max = A.max(axis=1, keepdims=True)
    thresholds = tau * per_cell_max
    active_mask = (A >= thresholds)
    active_count = active_mask.sum(axis=1)
    field_size_m2 = active_count.astype(float) * a_pix

    df_cells = pd.DataFrame({
        "cell_id": np.arange(K, dtype=int),
        "field_size_m2": field_size_m2,
        "threshold_frac": tau,
    })
    return df_cells


def metric2_coverage(df: pd.DataFrame, A_OCC: float, tau: float, env_id: str, K_hint: int | None = None) -> pd.DataFrame:
    """Metric 2: Coverage index at population level."""
    A, positions, _ = _extract_A_positions(df)

    per_cell_max = A.max(axis=1, keepdims=True)
    thresholds = tau * per_cell_max
    active_mask = (A >= thresholds)

    covered = active_mask.any(axis=0)
    n_active_cells = active_mask.sum(axis=0)
    max_activation = A.max(axis=0)
    sum_activation = A.sum(axis=0)

    df_positions = pd.DataFrame({
        "env_id": env_id,
        "K": int(K_hint) if K_hint is not None else int(A.shape[0]),
        "threshold_frac": tau,
        "x": positions[:, 0],
        "y": positions[:, 1],
        "covered": covered.astype(bool),
        "n_active_cells": n_active_cells.astype(int),
        "max_activation": max_activation.astype(float),
        "sum_activation": sum_activation.astype(float),
    })
    return df_positions


def metric3_redundancy(df_positions: pd.DataFrame) -> dict:
    """Metric 3: Redundancy distribution stats of active cells per position."""
    vals = df_positions["n_active_cells"].to_numpy(dtype=float)
    return {
        "redundancy_mean": float(np.mean(vals)),
        "redundancy_std": float(np.std(vals)),
        "redundancy_var": float(np.var(vals)),
        "redundancy_min": float(np.min(vals)),
        "redundancy_max": float(np.max(vals)),
        "redundancy_median": float(np.median(vals)),
    }


def metric4_sparseness(df: pd.DataFrame,
                       df_cells: pd.DataFrame | None,
                       df_positions: pd.DataFrame | None) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Metric 4: Lifetime and Population sparseness distribution stats."""
    A, positions, _ = _extract_A_positions(df)
    K, N = A.shape

    # Lifetime sparseness per cell
    rbar_c = np.mean(A, axis=1)
    mean_sq_c = np.mean(A ** 2, axis=1)
    S_life_c = np.divide(rbar_c ** 2, mean_sq_c, out=np.zeros_like(rbar_c), where=mean_sq_c > 0)

    # Population sparseness per position
    rbar_i = np.mean(A, axis=0)
    mean_sq_i = np.mean(A ** 2, axis=0)
    S_pop_i = np.divide(rbar_i ** 2, mean_sq_i, out=np.zeros_like(rbar_i), where=mean_sq_i > 0)

    stats = {
        "lifetime_sparseness_mean": float(np.mean(S_life_c)),
        "lifetime_sparseness_std": float(np.std(S_life_c)),
        "lifetime_sparseness_min": float(np.min(S_life_c)),
        "lifetime_sparseness_max": float(np.max(S_life_c)),
        "lifetime_sparseness_median": float(np.median(S_life_c)),
        "population_sparseness_mean": float(np.mean(S_pop_i)),
        "population_sparseness_std": float(np.std(S_pop_i)),
        "population_sparseness_min": float(np.min(S_pop_i)),
        "population_sparseness_max": float(np.max(S_pop_i)),
        "population_sparseness_median": float(np.median(S_pop_i)),
    }

    if df_cells is None:
        df_cells = pd.DataFrame({"cell_id": np.arange(K)})
    df_cells["lifetime_sparseness"] = S_life_c

    if df_positions is None:
        df_positions = pd.DataFrame({"x": positions[:, 0], "y": positions[:, 1]})
    df_positions["population_sparseness"] = S_pop_i

    return df_cells, df_positions, stats


def metric5_participation_ratio(df: pd.DataFrame, df_positions: pd.DataFrame | None) -> Tuple[pd.DataFrame, dict]:
    """Metric 5: Participation Ratio distribution stats (threshold-free)."""
    A, positions, _ = _extract_A_positions(df)
    num = np.sum(A ** 2, axis=0) ** 2
    den = np.sum(A ** 4, axis=0) + 1e-12
    PR_i = num / den

    stats = {
        "participation_ratio_mean": float(np.mean(PR_i)),
        "participation_ratio_std": float(np.std(PR_i)),
        "participation_ratio_min": float(np.min(PR_i)),
        "participation_ratio_max": float(np.max(PR_i)),
        "participation_ratio_median": float(np.median(PR_i)),
    }

    if df_positions is None:
        df_positions = pd.DataFrame({"x": positions[:, 0], "y": positions[:, 1]})
    df_positions["participation_ratio"] = PR_i
    return df_positions, stats


def metric6_skaggs_information(df: pd.DataFrame, df_cells: pd.DataFrame | None) -> Tuple[pd.DataFrame, dict]:
    """Metric 6: Skaggs spatial information per cell (bits) distribution stats."""
    A, _, _ = _extract_A_positions(df)
    K, N = A.shape
    eps = 1e-12

    rbar = np.mean(A, axis=1, keepdims=True)
    ratio = (A + eps) / (rbar + eps)
    Ic = (1.0 / N) * np.sum(ratio * np.log2(ratio), axis=1)

    stats = {
        "skaggs_mean_bits": float(np.mean(Ic)),
        "skaggs_std_bits": float(np.std(Ic)),
        "skaggs_min_bits": float(np.min(Ic)),
        "skaggs_max_bits": float(np.max(Ic)),
        "skaggs_median_bits": float(np.median(Ic)),
    }

    if df_cells is None:
        df_cells = pd.DataFrame({"cell_id": np.arange(K)})
    df_cells["skaggs_Ic_bits"] = Ic
    return df_cells, stats


# -----------------------------------------------------------------------------
# Compute all metrics for one K
# -----------------------------------------------------------------------------
def compute_all_metrics_for_df(df: pd.DataFrame, env_id: str, tau: float, A_OCC: float, K_hint: int | None = None):
    """Compute Metrics 1–6 for one network."""
    # Metric 1
    df_cells = metric1_place_field_size(df, A_OCC, tau)
    # Metric 2
    df_positions = metric2_coverage(df, A_OCC, tau, env_id, K_hint)
    # Metric 3
    redundancy_stats = metric3_redundancy(df_positions)
    # Metric 4
    df_cells, df_positions, sparse_stats = metric4_sparseness(df, df_cells, df_positions)
    # Metric 5
    df_positions, pr_stats = metric5_participation_ratio(df, df_positions)
    # Metric 6
    df_cells, skaggs_stats = metric6_skaggs_information(df, df_cells)

    # Coverage fraction (scalar)
    coverage_index = float(df_positions["covered"].mean()) if "covered" in df_positions.columns else np.nan

    # Mean field size (scalar) from Metric 1
    mean_field_size_m2 = float(df_cells["field_size_m2"].mean()) if "field_size_m2" in df_cells.columns else np.nan

    # Assemble a flat summary row for CSV (one row per K)
    row = {
        "env_id": env_id,
        "K": int(K_hint) if K_hint else len([c for c in df.columns if c.startswith("pc_")]),
        "tau": float(tau),
        "A_OCC": float(A_OCC),
        # Metric 1
        "mean_field_size_m2": mean_field_size_m2,
        # Metric 2
        "coverage_index": coverage_index,
        # Metric 3
        **redundancy_stats,
        # Metric 4
        **sparse_stats,
        # Metric 5
        **pr_stats,
        # Metric 6
        **skaggs_stats,
    }

    # Also return detailed tables for pickling
    return df_cells, df_positions, row


# -----------------------------------------------------------------------------
# Main script
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Compute Metrics 1–6 for multiple Visual Place Cell networks.")
    parser.add_argument("--pickle", required=True, type=Path,
                        help="Relative path (from REPO_ROOT) to activations pickle (dict[K]->DataFrame).")
    parser.add_argument("--env_id", required=True, type=str)
    parser.add_argument("--tau", default=0.20, type=float)
    parser.add_argument("--aocc", default=None, type=float)
    parser.add_argument("--klist", default=None, type=str)
    parser.add_argument("--outdir", default="data/metrics", type=Path)
    args = parser.parse_args()

    # Resolve paths relative to repo root
    pickle_path = (REPO_ROOT / args.pickle).resolve()
    outdir = (REPO_ROOT / args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Repo root: {REPO_ROOT}")
    print(f"[INFO] Loading:   {pickle_path}")

    with open(pickle_path, "rb") as f:
        data = pickle.load(f)
    if not isinstance(data, dict):
        raise ValueError("Expected pickle to contain dict[K]->DataFrame")

    K_list = [int(k.strip()) for k in args.klist.split(",")] if args.klist else sorted(int(k) for k in data.keys())

    results: Dict[int, dict] = {}
    rows = []

    for K in K_list:
        if K not in data:
            print(f"[WARN] K={K} not found; skipping.")
            continue

        df = data[K]

        # Occupiable area
        if args.aocc is None:
            pos = df[["x", "y"]].to_numpy(float)
            xmin, ymin = pos.min(axis=0)
            xmax, ymax = pos.max(axis=0)
            A_OCC = float((xmax - xmin) * (ymax - ymin))
        else:
            A_OCC = float(args.aocc)

        df_cells, df_positions, row = compute_all_metrics_for_df(
            df, env_id=args.env_id, tau=float(args.tau), A_OCC=A_OCC, K_hint=K
        )
        results[K] = {"df_cells": df_cells, "df_positions": df_positions, "summary_row": row}
        rows.append(row)
        print(f"[OK] K={K}  coverage={row['coverage_index']:.3f}  PR_mean={row['participation_ratio_mean']:.3f}")

    # Combined pickle (detailed tables per K)
    combined_pickle = outdir / "metrics_all.pkl"
    with open(combined_pickle, "wb") as f:
        pickle.dump(results, f)
    print(f"[SAVE] Combined results -> {combined_pickle}")

    # Single-row-per-K CSV with descriptive headers
    df_csv = pd.DataFrame(rows).sort_values("K").reset_index(drop=True)
    csv_path = outdir / "metrics_summary.csv"
    df_csv.to_csv(csv_path, index=False)
    print(f"[SAVE] Summary CSV (1 row per K) -> {csv_path}")


if __name__ == "__main__":
    main()
