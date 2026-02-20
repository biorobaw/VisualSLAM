import os
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

# =============================================================================
# Config (absolute paths + environment)
# =============================================================================
REPO_ROOT = Path(__file__).resolve().parents[3]

# Avoid BLAS oversubscription under process parallelism
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

# Experiment selection
MAZES = ['LM4', 'LM6', 'LM8', 'LM8D', 'LMO8', 'LM8_addition', 'LMO8_test', 'BR']
MAZE_INDEX = 4  # LM8
MAZE_KEY = MAZES[MAZE_INDEX]

# Network sizes to evaluate
# N_PCS_LIST = [10, 25, 50, 75, 100, 250, 500, 750]
N_PCS_LIST = [10, 25, 50, 75, 100, 250, 500, 750]
# Feature choice in your dataset: "cnn" or "multimodel"
FEATURE_TYPE = "multimodel"

# I/O
TRAIN_PATH      = REPO_ROOT / f"data/VisualPlaceCellData/{MAZE_KEY}_Training"
CLUSTER_DIR     = REPO_ROOT / "data/VisualPlaceCellData/VisualPlaceCellClusters"
FIG_PREFIX_DIR  = REPO_ROOT / "data/figures/ActivationMaps"
BG_IMAGE        = REPO_ROOT / f"data/DataCache/{MAZE_KEY}.png"
ACTIVATIONS_OUT = REPO_ROOT / f"data/activations/activations_{MAZE_KEY}.pkl"

# TRAIN_PATH      = REPO_ROOT / f"data/VisualPlaceCellData/LMO8_testWall_Testing"
# CLUSTER_DIR     = REPO_ROOT / "data/VisualPlaceCellData/VisualPlaceCellClusters"
# FIG_PREFIX_DIR  = REPO_ROOT / "data/figures/ActivationMaps"
# BG_IMAGE        = REPO_ROOT / f"data/DataCache/LMO8_testWall_Testing"
# ACTIVATIONS_OUT = REPO_ROOT / f"data/activations/activations_LMO8_test.pkl"

# Plotting controls
MAKE_FIGS = True          # set False to skip plotting entirely (fastest)
PLOT_TOP_K = 0            # 0 = plot all PCs; else plot top-K by activation variance

# =============================================================================
# Utils
# =============================================================================

def _resolve_cluster_path(base_dir: Path, file_stem: str) -> Path:
    tried = []
    for ext in ("", ".pkl", ".pickle", ".bin"):
        cand = (base_dir / file_stem).with_suffix(ext)
        tried.append(str(cand))
        if cand.exists():
            return cand
    raise FileNotFoundError(
        f"Could not find cluster file for stem '{file_stem}'. Tried:\n  " +
        "\n  ".join(tried)
    )

def _load_bg_image(image_path: Path, flip_vertical: bool = True) -> np.ndarray:
    arr = np.asarray(Image.open(image_path).convert("RGB"))
    if flip_vertical:
        arr = np.flipud(arr)  # +Y up
    return arr

def _stack_features(test_data, feature_type: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (X, x_coords, y_coords)
    X: (N_obs, D) float32 feature matrix
    """
    feats = []
    xs, ys = [], []
    if feature_type == "cnn":
        for obs in test_data.observations:
            feats.append(np.asarray(obs.cnn_feature_vector, dtype=np.float32, copy=False))
            xs.append(obs.x); ys.append(obs.y)
    else:
        for obs in test_data.observations:
            feats.append(np.asarray(obs.multimodal_feature_vector, dtype=np.float32, copy=False))
            xs.append(obs.x); ys.append(obs.y)
    X = np.vstack(feats).astype(np.float32, copy=False)
    return X, np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32)

def _load_centers_radii(n_pcs: int, maze_key: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Loads clusters as (centers, radii) arrays.
    centers: (K, D) float32
    radii:   (K,)   float32  (interpreted as sigma for Gaussian RBF)
    """
    file_stem = f"multimodal_gmm_{n_pcs}_clusters_{maze_key}"
    path = _resolve_cluster_path(CLUSTER_DIR, file_stem)
    with open(path, "rb") as fh:
        clusters = pickle.load(fh)  # iterable of (center, radius)

    centers = np.vstack([np.asarray(c, dtype=np.float32) for (c, r) in clusters])
    radii   = np.asarray([float(r) if r != 0 else 1.0 for (c, r) in clusters], dtype=np.float32)
    return centers, radii

def _pairwise_squared_distances(X: np.ndarray, C: np.ndarray) -> np.ndarray:
    """
    Efficient pairwise squared Euclidean distances between rows of X and C.
    X: (N, D), C: (K, D)  ->  D2: (N, K)
    Uses: ||x - c||^2 = ||x||^2 + ||c||^2 - 2 x·c
    """
    # Make sure float32 for speed/memory
    X = np.asarray(X, dtype=np.float32, order="C")
    C = np.asarray(C, dtype=np.float32, order="C")

    x2 = np.sum(X * X, axis=1, keepdims=True)           # (N,1)
    c2 = np.sum(C * C, axis=1, keepdims=True).T         # (1,K)
    XC = X @ C.T                                        # (N,K)
    D2 = x2 + c2 - 2.0 * XC
    # Numerical safety: distances should be >= 0
    np.maximum(D2, 0.0, out=D2)
    return D2

def _gaussian_rbf_from_d2(D2: np.ndarray, sigmas: np.ndarray) -> np.ndarray:
    """
    Apply Gaussian RBF with per-column sigma.
    D2: (N,K) squared distances
    sigmas: (K,) per-place-cell sigma (radius)
    """
    # If your kernel differs, change the next line accordingly.
    denom = 2.0 * (np.asarray(sigmas, dtype=np.float32) ** 2)  # (K,)
    A = np.exp(-D2 / denom[None, :], dtype=np.float32)
    return A

def _minmax_normalize_cols(A: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """ Min-max normalize each column to [0,1] """
    col_min = A.min(axis=0, keepdims=True)
    col_max = A.max(axis=0, keepdims=True)
    scale = np.maximum(col_max - col_min, eps)
    return (A - col_min) / scale

def _activations_dataframe(X: np.ndarray, xs: np.ndarray, ys: np.ndarray, centers: np.ndarray, radii: np.ndarray) -> pd.DataFrame:
    """
    Vectorized activation computation: returns DataFrame with columns [x, y, pc_0..pc_{K-1}]
    """
    D2 = _pairwise_squared_distances(X, centers)        # (N,K)
    A  = _gaussian_rbf_from_d2(D2, radii)               # (N,K)
    A  = _minmax_normalize_cols(A)                      # match "normalized(..., 'min_max')"

    cols = {f"pc_{i}": A[:, i] for i in range(A.shape[1])}
    df = pd.DataFrame({"x": xs, "y": ys, **cols})
    return df

def _select_top_k_cols_by_variance(df: pd.DataFrame, k: int) -> pd.DataFrame:
    if k <= 0:
        return df
    pc_cols = [c for c in df.columns if c.startswith("pc_")]
    vars_ = df[pc_cols].var(axis=0)
    top = vars_.nlargest(min(k, len(pc_cols))).index.tolist()
    return df[["x", "y"] + top]

def plot_place_cell_activation_maps_colored(
    activations_df: pd.DataFrame,
    output_file_prefix: Path,
    image_path: Path,
    image_alpha: float = 0.55,
    vmin: float = 0.0,
    vmax: float = 1.0,
    cmap: str = "viridis",
    flip_image_vertical: bool = True,
    rasterized: bool = True,
    show_colorbar: bool = False,
) -> None:
    x = activations_df["x"].to_numpy()
    y = activations_df["y"].to_numpy()
    bg = _load_bg_image(image_path, flip_vertical=flip_image_vertical) if image_path.exists() else None

    pc_cols = [c for c in activations_df.columns if c.startswith("pc_")]
    K = len(pc_cols)
    nrows = int(np.ceil(K / 5))
    ncols = 5
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 3.0, nrows * 3.0))
    axes = np.atleast_1d(axes).ravel()

    # Estimate extents from data spread (fallback if no world size provided)
    xpad = (x.max() - x.min()) * 0.05 if x.size else 1.0
    ypad = (y.max() - y.min()) * 0.05 if y.size else 1.0
    extent = [x.min() - xpad, x.max() + xpad, y.min() - ypad, y.max() + ypad]

    for i, pc in enumerate(pc_cols):
        ax = axes[i]
        if bg is not None:
            ax.imshow(bg, extent=extent, origin="lower", alpha=image_alpha, zorder=0)
        sc = ax.scatter(x, y, s=8, c=activations_df[pc].to_numpy(), cmap=cmap, vmin=vmin, vmax=vmax, zorder=1, rasterized=rasterized)
        ax.set_title(pc, fontsize=9)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.set_xticks([]); ax.set_yticks([])
        if show_colorbar:
            plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)

    for j in range(K, len(axes)):
        axes[j].axis("off")

    fig.tight_layout()
    output_file_prefix.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_prefix.with_suffix(".png"), dpi=200)
    plt.close()

# =============================================================================
# Worker
# =============================================================================

def compute_and_plot_for_n(n_pcs: int, maze_key: str, test_data, feature_type: str) -> Tuple[int, pd.DataFrame]:
    # Load data vectors (N,D) and (K,D)
    X, xs, ys = _stack_features(test_data, feature_type)
    centers, radii = _load_centers_radii(n_pcs, maze_key)

    # Vectorized activations
    df = _activations_dataframe(X, xs, ys, centers, radii)

    # Optional: plot all or top-K PCs
    if MAKE_FIGS:
        if PLOT_TOP_K > 0:
            df_plot = _select_top_k_cols_by_variance(df, PLOT_TOP_K)
        else:
            df_plot = df
        out_prefix = FIG_PREFIX_DIR / f"network_{n_pcs}_{maze_key}_pc_activation_map"
        plot_place_cell_activation_maps_colored(
            df_plot, output_file_prefix=out_prefix, image_path=BG_IMAGE,
            show_colorbar=False, rasterized=True
        )

    return n_pcs, df


def _nearest_row_index(df: pd.DataFrame, x0: float, y0: float) -> int:
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    d2 = (x - x0) ** 2 + (y - y0) ** 2
    return int(np.argmin(d2))


def _pc_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("pc_")]


def select_initial_pc_by_peak_near_center(df: pd.DataFrame) -> tuple[str, tuple[float, float]]:
    """
    For the smallest K network:
      - find each PC's peak (x*, y*)
      - select the PC whose peak is closest to maze center

    Special case:
      - if MAZE_KEY == "LMO8", force pc_2
    """
    pc_cols = [c for c in df.columns if c.startswith("pc_")]

    # ---- LMO8 override ----
    if MAZE_KEY == "LMO8":
        forced_pc = "pc_1"
        if forced_pc not in pc_cols:
            raise ValueError(f"{forced_pc} not found in activations dataframe")
        a = df[forced_pc].to_numpy()
        idx = int(np.argmax(a))
        peak_xy = (float(df["x"].iat[idx]), float(df["y"].iat[idx]))
        return forced_pc, peak_xy
    # ----------------------

    # original behavior
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    x_center = float(np.median(x))
    y_center = float(np.median(y))

    best_pc = None
    best_peak = None
    best_d2 = float("inf")

    for pc in pc_cols:
        a = df[pc].to_numpy()
        idx = int(np.argmax(a))
        px, py = float(x[idx]), float(y[idx])
        d2 = (px - x_center) ** 2 + (py - y_center) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best_pc = pc
            best_peak = (px, py)

    return best_pc, best_peak


def select_pc_max_at_anchor(df: pd.DataFrame, anchor_xy: tuple[float, float]) -> str:
    """
    Choose the PC with highest activation at the sampled point nearest to anchor_xy.
    """
    ix = _nearest_row_index(df, anchor_xy[0], anchor_xy[1])
    pc_cols = _pc_cols(df)
    vals = df.loc[ix, pc_cols].to_numpy(dtype=np.float32)
    return pc_cols[int(np.argmax(vals))]

def build_tracked_pc_chain(results: dict[int, pd.DataFrame]) -> tuple[list[int], list[str], tuple[float, float]]:
    """
    results: {K: activations_df}
    Returns:
      Ks_sorted, pcs_selected_per_K, anchor_xy (fixed)
    """
    Ks = sorted(results.keys())
    df0 = results[Ks[0]]

    pc0, anchor_xy = select_initial_pc_by_peak_near_center(df0)

    pcs = [pc0]
    for K in Ks[1:]:
        df = results[K]
        pcs.append(select_pc_max_at_anchor(df, anchor_xy))

    return Ks, pcs, anchor_xy

def plot_tracked_chain(results: dict[int, pd.DataFrame], maze_key: str, out_file: Path,
                       image_path: Path, cmap: str = "viridis"):
    Ks, pcs, anchor_xy = build_tracked_pc_chain(results)

    # Use common extent from first df (same sampling assumed)
    df0 = results[Ks[0]]
    x = df0["x"].to_numpy()
    y = df0["y"].to_numpy()
    xpad = (x.max() - x.min()) * 0.05
    ypad = (y.max() - y.min()) * 0.05
    extent = [x.min() - xpad, x.max() + xpad, y.min() - ypad, y.max() + ypad]

    bg = _load_bg_image(image_path, flip_vertical=True) if image_path.exists() else None

    ncols = len(Ks)
    fig, axes = plt.subplots(nrows=1, ncols=ncols, figsize=(ncols*2.4, 4.0))
    axes = np.atleast_1d(axes)

    for ax, K, pc in zip(axes, Ks, pcs):
        df = results[K]
        xx = df["x"].to_numpy()
        yy = df["y"].to_numpy()

        if bg is not None:
            ax.imshow(bg, extent=extent, origin="lower", zorder=0)

        ax.scatter(xx, yy, s=8, c=df[pc].to_numpy(), cmap=cmap, vmin=0.0, vmax=1.0, alpha=0.5,
                   zorder=1, rasterized=True)

        # mark the anchor point
        # ax.scatter([anchor_xy[0]], [anchor_xy[1]], s=30, c="red", zorder=2)

        ax.set_title(f"{maze_key}   K={K})",
                     fontsize=9)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.set_xticks([]); ax.set_yticks([])

    fig.tight_layout()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=300)
    plt.close(fig)




# =============================================================================
# Main
# =============================================================================

def main(max_workers: int | None = None) -> None:
    print(f"Repo root: {REPO_ROOT}")
    print(f"Loading test data: {TRAIN_PATH}")
    with open(TRAIN_PATH, "rb") as fh:
        test_data = pickle.load(fh)

    results: Dict[int, pd.DataFrame] = {}

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(compute_and_plot_for_n, n, MAZE_KEY, test_data, FEATURE_TYPE): n for n in N_PCS_LIST}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Networks"):
            n_key = futures[fut]
            n, df = fut.result()
            results[n] = df

    ACTIVATIONS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ACTIVATIONS_OUT, "wb") as fh:
        pickle.dump(results, fh, protocol=pickle.HIGHEST_PROTOCOL)

    plot_tracked_chain(
        results=results,  # {K: df} for that maze
        maze_key=MAZE_KEY,
        out_file=FIG_PREFIX_DIR / f"{MAZE_KEY}_field_vs_k.png",
        image_path=BG_IMAGE,
    )

    print("Finished.")
    print(f"Figures → {FIG_PREFIX_DIR}/network_{{N}}_{MAZE_KEY}_pc_activation_map.png (if enabled)")
    print(f"Activations pickle → {ACTIVATIONS_OUT}")

if __name__ == "__main__":
    # Use all logical cores; cap if RAM is tight.
    main(max_workers=8)
