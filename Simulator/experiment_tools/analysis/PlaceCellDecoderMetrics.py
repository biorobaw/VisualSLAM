"""
Batch spatial decoding with Kernel Ridge (RBF)
------------------------------------------------
Processes activation datasets to evaluate spatial decoding accuracy.

Directory layout (default):
    REPO_ROOT/
      data/
        activations/
          activations_LM8.pkl
        results/
          LM8/
            spatial_decoders/
              spatial_decoder_summary_LM8.csv
              plots/
                cdf_errors_LM8_250.png
                scatter_true_vs_pred_LM8_250.png
Author: Chance J. Hamilton / VPCE Project
"""

from __future__ import annotations
from pathlib import Path
import argparse
import pickle
import json
import sys
import warnings

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import train_test_split

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ==========================================================
# Utilities
# ==========================================================

RNG_DEFAULT = 42

def euclidean_errors(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    return np.sqrt(((y_true - y_pred) ** 2).sum(axis=1))

def summarize_errors(err: np.ndarray) -> dict:
    return {
        "mae": float(np.mean(err)),
        "median": float(np.median(err)),
        "p75": float(np.percentile(err, 75)),
        "p90": float(np.percentile(err, 90)),
        "max": float(np.max(err)),
        "n": int(err.size),
    }

def median_heuristic_gamma(X: np.ndarray, max_samples: int = 2000, rng: int = RNG_DEFAULT) -> float:
    """Approximate kernel width via the median heuristic."""
    n = X.shape[0]
    m = min(n, max_samples)
    idx = np.random.default_rng(rng).choice(n, size=m, replace=False)
    Z = X[idx]
    G = Z @ Z.T
    s = np.sum(Z**2, axis=1, keepdims=True)
    D2 = s - 2 * G + s.T
    tri = D2[np.triu_indices_from(D2, k=1)]
    med = np.median(tri)
    return 1.0 / med if np.isfinite(med) and med > 0 else 1.0

def make_plots(outdir: Path, maze_key: str, n_pcs: int,
               y_true_test: np.ndarray, y_pred_test: np.ndarray, errs: np.ndarray) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    # Scatter plot
    plt.figure(figsize=(5.4, 5.4))
    plt.scatter(y_true_test[:, 0], y_true_test[:, 1], s=10, alpha=0.6, label="True")
    plt.scatter(y_pred_test[:, 0], y_pred_test[:, 1], s=10, alpha=0.6, label="Pred")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.title(f"KRR(RBF) — True vs Pred (Test)\nMaze={maze_key}  PCs={n_pcs}")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / f"scatter_true_vs_pred_{maze_key}_{n_pcs}.png", dpi=160)
    plt.close()

    # CDF plot
    sorted_e = np.sort(errs)
    cdf = np.arange(1, sorted_e.size + 1) / sorted_e.size
    plt.figure(figsize=(6.2, 4.2))
    plt.plot(sorted_e, cdf, linewidth=2)
    plt.xlabel("Euclidean error (m)")
    plt.ylabel("CDF")
    plt.title(f"Error CDF — KRR(RBF)\nMaze={maze_key}  PCs={n_pcs}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / f"cdf_errors_{maze_key}_{n_pcs}.png", dpi=160)
    plt.close()

def make_superimposed_cdf_plot(df_maze: pd.DataFrame, outdir: Path, maze_key: str) -> None:
    """
    Creates a single CDF plot with all network sizes superimposed.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 5))

    # Loop over each network row, load its raw test errors
    for _, row in df_maze.iterrows():
        errs = np.array(row["test_errors"])
        sorted_e = np.sort(errs)
        cdf = np.arange(1, sorted_e.size + 1) / sorted_e.size
        plt.plot(sorted_e, cdf, linewidth=2, label=f"N={row['network_size']}")

    plt.xlabel("Euclidean error (m)")
    plt.ylabel("CDF")
    plt.title(f"Spatial Decoding CDFs\nMaze={maze_key}")
    plt.grid(True, alpha=0.3)
    plt.legend(title="Network Size", fontsize=8)
    plt.tight_layout()

    plt.savefig(outdir / f"cdf_superimposed_{maze_key}.png", dpi=160)
    plt.close()

# ==========================================================
# Core functions
# ==========================================================

def process_one_network(df: pd.DataFrame, maze_key: str, n_pcs: int,
                        test_size: float, val_size: float, seed: int,
                        alpha: float, gamma_center: float | None,
                        gamma_mults: list[float], make_plots_flag: bool,
                        plots_dir: Path) -> dict:
    """Train + evaluate a single KRR(RBF) decoder."""
    pc_cols = [c for c in df.columns if c.startswith("pc_")]
    X = df[pc_cols].to_numpy(np.float32)
    Y = df[["x", "y"]].to_numpy(np.float32)

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
    X_tr, X_val, y_tr, y_val = train_test_split(X_train, y_train, test_size=val_size, random_state=seed)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    if gamma_center is None:
        gamma_center = median_heuristic_gamma(X_tr_s, rng=seed)

    best = None
    for g in gamma_center * np.array(gamma_mults, dtype=float):
        model = KernelRidge(kernel="rbf", alpha=alpha, gamma=float(g))
        model.fit(X_tr_s, y_tr)
        y_val_hat = model.predict(X_val_s)
        val_err = euclidean_errors(y_val, y_val_hat)
        mae = float(np.mean(val_err))
        if best is None or mae < best["val_mae"]:
            best = {"gamma": float(g), "val_mae": mae, "val_median": float(np.median(val_err)),
                    "val_p75": float(np.percentile(val_err, 75))}

    # Final fit and test
    X_trval_s = np.vstack([X_tr_s, X_val_s])
    y_trval = np.vstack([y_tr, y_val])
    final = KernelRidge(kernel="rbf", alpha=alpha, gamma=best["gamma"])
    final.fit(X_trval_s, y_trval)
    y_test_hat = final.predict(X_test_s)
    test_err = euclidean_errors(y_test, y_test_hat)
    test_summary = summarize_errors(test_err)

    if make_plots_flag:
        make_plots(plots_dir, maze_key, n_pcs, y_test, y_test_hat, test_err)

    return {
        "maze_key": maze_key,
        "network_size": int(n_pcs),

        # Store raw errors for multi-network CDF
        "test_errors": test_err.tolist(),

        # Relevant metrics only
        "test_mae": float(np.mean(test_err)),
        "test_median": float(np.median(test_err)),
    }


def process_one_maze(pkl_path: Path, repo_root: Path,
                     alpha: float, gamma_center: float | None,
                     gamma_mults: list[float], test_size: float,
                     val_size: float, seed: int, make_plots_flag: bool) -> pd.DataFrame:
    """Process all network sizes for one maze."""
    maze_key = pkl_path.stem.replace("activations_", "")
    with open(pkl_path, "rb") as f:
        act_dict = pickle.load(f)

    # Default output path under data/results/{MAZE_KEY}/spatial_decoders/
    maze_out_dir = repo_root / "data" / "results" / maze_key / "spatial_decoders"
    plots_dir = maze_out_dir / "plots"
    maze_out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for n_pcs, df in act_dict.items():
        row = process_one_network(df, maze_key, int(n_pcs),
                                  test_size, val_size, seed,
                                  alpha, gamma_center,
                                  gamma_mults, make_plots_flag, plots_dir)
        rows.append(row)

    df_maze = pd.DataFrame(rows).sort_values("network_size")

    # Save compact CSV (only relevant metrics)
    df_save = df_maze.drop(columns=["test_errors"])
    df_save.to_csv(maze_out_dir / f"spatial_decoder_summary_{maze_key}.csv", index=False)

    # Plot multi-network CDF
    make_superimposed_cdf_plot(df_maze, maze_out_dir / "plots", maze_key)

    return df_maze


# ==========================================================
# CLI
# ==========================================================

def main():
    parser = argparse.ArgumentParser(description="Batch KRR(RBF) spatial decoders.")
    parser.add_argument("--repo-root", type=str, default=None, help="Repo root (defaults to Path.cwd().parents[2]).")
    parser.add_argument("--activations-dir", type=str, default=None,
                        help="Directory with activations_*.pkl (default: {REPO_ROOT}/data/activations).")
    parser.add_argument("--alpha", type=float, default=1e-1, help="Regularization strength.")
    parser.add_argument("--gamma", type=float, default=None, help="Optional fixed gamma.")
    parser.add_argument("--gamma-mults", type=str, default="0.3,1.0,3.0", help="Comma-separated multipliers.")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split fraction.")
    parser.add_argument("--val-size", type=float, default=0.2, help="Validation fraction of train.")
    parser.add_argument("--seed", type=int, default=RNG_DEFAULT, help="Random seed.")
    parser.add_argument("--make-plots", action="store_true", help="Save scatter and CDF plots.")
    parser.add_argument("--maze-keys", type=str, default=None, help="Comma-separated maze names to process.")
    args = parser.parse_args()

    REPO_ROOT = Path(args.repo_root).resolve() if args.repo_root else Path.cwd().parents[2]
    ACT_DIR = Path(args.activations_dir).resolve() if args.activations_dir else REPO_ROOT / "data" / "activations"

    all_pkls = sorted(ACT_DIR.glob("activations_*.pkl"))
    if args.maze_keys:
        wanted = {k.strip() for k in args.maze_keys.split(",")}
        pkls = [p for p in all_pkls if p.stem.replace("activations_", "") in wanted]
    else:
        pkls = all_pkls
    if not pkls:
        print(f"No activation pickles found in {ACT_DIR}", file=sys.stderr)
        sys.exit(1)

    gamma_mults = [float(x) for x in args.gamma_mults.split(",")]
    gamma_center = float(args.gamma) if args.gamma is not None else None

    all_results = []
    for pkl_path in pkls:
        df_maze = process_one_maze(pkl_path, REPO_ROOT, args.alpha,
                                   gamma_center, gamma_mults,
                                   args.test_size, args.val_size,
                                   args.seed, args.make_plots)
        all_results.append(df_maze)

    # Combine and save global summary
    agg = pd.concat(all_results, ignore_index=True)
    out_path = REPO_ROOT / "data" / "results" / "spatial_decoder_summary_ALL.csv"
    agg.sort_values(["maze_key", "network_size"]).to_csv(out_path, index=False)
    print(f"All results written to: {out_path}")


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    main()
