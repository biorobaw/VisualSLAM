#!/usr/bin/env python3
"""
Standalone ATE/RPE computation for ORB-SLAM3 results.
No external dependencies beyond numpy and pandas.
Implements Umeyama alignment (sim(3)) and standard ATE/RPE metrics.
"""

import os
import glob
import re
import numpy as np
import csv
from pathlib import Path


# ── TUM file I/O ──────────────────────────────────────────────────────────────

def read_tum(filepath):
    """Read a TUM-format trajectory file.  Returns (timestamps, positions_Nx3, quats_Nx4)."""
    ts, pos, quat = [], [], []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            ts.append(float(parts[0]))
            pos.append([float(parts[1]), float(parts[2]), float(parts[3])])
            quat.append([float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])])
    return np.array(ts), np.array(pos), np.array(quat)


def associate_trajectories(ts_gt, pos_gt, ts_est, pos_est, max_diff=0.5):
    """Associate GT and estimated trajectories by nearest timestamp.
    Returns matched (gt_positions, est_positions)."""
    matches_gt, matches_est = [], []
    for i, t_est in enumerate(ts_est):
        diffs = np.abs(ts_gt - t_est)
        j = np.argmin(diffs)
        if diffs[j] <= max_diff:
            matches_gt.append(pos_gt[j])
            matches_est.append(pos_est[i])
    return np.array(matches_gt), np.array(matches_est)


# ── Umeyama alignment (sim(3)) ───────────────────────────────────────────────

def umeyama_alignment(src, dst):
    """Umeyama alignment: finds s, R, t  such that  dst ≈ s·R·src + t.
    src, dst: Nx3.  Returns (s, R_3x3, t_3x1)."""
    assert src.shape == dst.shape
    n, d = src.shape

    mu_src = src.mean(axis=0)
    mu_dst = dst.mean(axis=0)

    src_demean = src - mu_src
    dst_demean = dst - mu_dst

    sigma_src_sq = np.mean(np.sum(src_demean ** 2, axis=1))
    Sigma = (dst_demean.T @ src_demean) / n

    U, D, Vt = np.linalg.svd(Sigma)

    S = np.eye(d)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[d - 1, d - 1] = -1

    R = U @ S @ Vt
    s = np.trace(np.diag(D) @ S) / sigma_src_sq
    t = mu_dst - s * R @ mu_src

    return s, R, t


def align_trajectories(gt, est):
    """Align est to gt using Umeyama sim(3).  Returns aligned_est."""
    s, R, t = umeyama_alignment(est, gt)
    return s * (R @ est.T).T + t


# ── Metric computation ────────────────────────────────────────────────────────

def compute_ate(gt, est_aligned):
    """ATE (translational) after alignment.  Returns dict of stats."""
    errors = np.linalg.norm(gt - est_aligned, axis=1)
    return {
        'rmse': float(np.sqrt(np.mean(errors ** 2))),
        'mean': float(np.mean(errors)),
        'median': float(np.median(errors)),
        'min': float(np.min(errors)),
        'max': float(np.max(errors)),
    }


def compute_rpe_trans(gt, est_aligned, delta=1):
    """RPE translational (frame-to-frame).  Returns dict of stats."""
    errors = []
    for i in range(len(gt) - delta):
        gt_rel = gt[i + delta] - gt[i]
        est_rel = est_aligned[i + delta] - est_aligned[i]
        errors.append(np.linalg.norm(gt_rel - est_rel))
    errors = np.array(errors)
    if len(errors) == 0:
        return None
    return {
        'rmse': float(np.sqrt(np.mean(errors ** 2))),
        'mean': float(np.mean(errors)),
        'median': float(np.median(errors)),
        'min': float(np.min(errors)),
        'max': float(np.max(errors)),
    }


def rotation_matrix_from_quat(q):
    """Convert quaternion [qx, qy, qz, qw] to 3x3 rotation matrix."""
    x, y, z, w = q
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - z*w),     2*(x*z + y*w)],
        [2*(x*y + z*w),     1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w),     2*(y*z + x*w),     1 - 2*(x*x + y*y)],
    ])


def compute_rpe_rot(ts_gt, quat_gt, ts_est, quat_est, pos_gt_matched, pos_est_matched, delta=1):
    """RPE rotational in degrees (frame-to-frame).  Uses matched quaternions."""
    # We need quats matched by the same association used for positions
    # For simplicity, re-associate to get matched quats
    errors = []
    n = min(len(quat_gt), len(quat_est))
    for i in range(n - delta):
        R_gt_i = rotation_matrix_from_quat(quat_gt[i])
        R_gt_j = rotation_matrix_from_quat(quat_gt[i + delta])
        R_est_i = rotation_matrix_from_quat(quat_est[i])
        R_est_j = rotation_matrix_from_quat(quat_est[i + delta])

        R_gt_rel = R_gt_j @ R_gt_i.T
        R_est_rel = R_est_j @ R_est_i.T

        R_err = R_gt_rel @ R_est_rel.T
        trace_val = np.clip((np.trace(R_err) - 1.0) / 2.0, -1.0, 1.0)
        angle_deg = np.degrees(np.arccos(trace_val))
        errors.append(angle_deg)

    errors = np.array(errors)
    if len(errors) == 0:
        return None
    return {
        'rmse': float(np.sqrt(np.mean(errors ** 2))),
        'mean': float(np.mean(errors)),
        'median': float(np.median(errors)),
        'min': float(np.min(errors)),
        'max': float(np.max(errors)),
    }


# ── Sequence name extraction ──────────────────────────────────────────────────

def extract_sequence_name(est_path, results_root):
    """Extract human-readable sequence name from path structure."""
    rel = os.path.relpath(est_path, results_root)
    parts = rel.split(os.sep)
    # Pattern: <seq_group>/<sub_seq>/<date>/<run>/estimation.tum  (sim worlds)
    # Pattern: <seq>/<date>/<run>/estimation.tum  (oxford)
    if len(parts) >= 5 and parts[0].startswith(('2)', '3)')):
        return parts[1]  # e.g. city_sim_day_centerline
    elif len(parts) >= 4:
        return parts[0]  # e.g. 1)ORC-sun-...
    return parts[0]


def extract_date_run(est_path, results_root):
    """Extract date and run number from path."""
    rel = os.path.relpath(est_path, results_root)
    parts = rel.split(os.sep)
    # Find date pattern YYYY-MM-DD and run number
    date, run = "unknown", "unknown"
    for p in parts:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', p):
            date = p
        elif re.match(r'^\d+$', p):
            run = p
    return date, run


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    results_root = os.path.join(os.path.dirname(__file__), 'results')
    output_csv = os.path.join(results_root, 'metrics_summary.csv')

    est_files = sorted(glob.glob(os.path.join(results_root, '**', 'estimation.tum'), recursive=True))

    print(f"Found {len(est_files)} estimation files")

    rows = []
    for est_path in est_files:
        gt_path = os.path.join(os.path.dirname(est_path), 'groundtruth.tum')
        if not os.path.exists(gt_path):
            print(f"  SKIP (no GT): {est_path}")
            continue

        sequence = extract_sequence_name(est_path, results_root)
        date, run = extract_date_run(est_path, results_root)

        print(f"  Processing: {sequence}  date={date}  run={run}")

        try:
            ts_gt, pos_gt, quat_gt = read_tum(gt_path)
            ts_est, pos_est, quat_est = read_tum(est_path)

            if len(ts_est) < 3 or len(ts_gt) < 3:
                print(f"    Too few poses ({len(ts_est)} est, {len(ts_gt)} gt). Skipping.")
                continue

            gt_matched, est_matched = associate_trajectories(ts_gt, pos_gt, ts_est, pos_est)

            if len(gt_matched) < 3:
                print(f"    Too few matched poses ({len(gt_matched)}). Skipping.")
                continue

            # Also associate quaternions for RPE rotation
            quat_gt_matched, quat_est_matched = [], []
            for i, t_est in enumerate(ts_est):
                diffs = np.abs(ts_gt - t_est)
                j = np.argmin(diffs)
                if diffs[j] <= 0.5:
                    quat_gt_matched.append(quat_gt[j])
                    quat_est_matched.append(quat_est[i])
            quat_gt_matched = np.array(quat_gt_matched)
            quat_est_matched = np.array(quat_est_matched)

            est_aligned = align_trajectories(gt_matched, est_matched)

            ate = compute_ate(gt_matched, est_aligned)
            rpe_t = compute_rpe_trans(gt_matched, est_aligned)
            rpe_r = compute_rpe_rot(ts_gt, quat_gt_matched, ts_est, quat_est_matched,
                                     gt_matched, est_matched)

            if ate and rpe_t and rpe_r:
                rows.append({
                    'Sequence': sequence,
                    'Date': date,
                    'Run': run,
                    'Modality': 'mono',
                    'Matched_Poses': len(gt_matched),
                    'ATE_Trans_RMSE': round(ate['rmse'], 6),
                    'ATE_Trans_Mean': round(ate['mean'], 6),
                    'ATE_Trans_Median': round(ate['median'], 6),
                    'ATE_Trans_Min': round(ate['min'], 6),
                    'ATE_Trans_Max': round(ate['max'], 6),
                    'RPE_Trans_RMSE': round(rpe_t['rmse'], 6),
                    'RPE_Trans_Mean': round(rpe_t['mean'], 6),
                    'RPE_Trans_Median': round(rpe_t['median'], 6),
                    'RPE_Trans_Min': round(rpe_t['min'], 6),
                    'RPE_Trans_Max': round(rpe_t['max'], 6),
                    'RPE_Rot_RMSE': round(rpe_r['rmse'], 6),
                    'RPE_Rot_Mean': round(rpe_r['mean'], 6),
                    'RPE_Rot_Median': round(rpe_r['median'], 6),
                    'RPE_Rot_Min': round(rpe_r['min'], 6),
                    'RPE_Rot_Max': round(rpe_r['max'], 6),
                })
                print(f"    ATE RMSE={ate['rmse']:.4f}  RPE_t RMSE={rpe_t['rmse']:.4f}  RPE_r RMSE={rpe_r['rmse']:.4f}")
            else:
                print(f"    Metrics computation incomplete. Skipping.")

        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    if rows:
        fieldnames = list(rows[0].keys())
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {len(rows)} rows to {output_csv}")
    else:
        print("No metrics computed.")


if __name__ == '__main__':
    main()
