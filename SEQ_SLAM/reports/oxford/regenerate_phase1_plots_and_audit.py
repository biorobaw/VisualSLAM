import csv
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from seqslam import SeqSLAM
from tune_oxford import _prepare_params, _plot_matches

ROOT = "/Users/asadbeknematov/Desktop/Projects/VisualSLAM"
PYSEQSLAM_DIR = os.path.join(ROOT, "SEQ_SLAM/pyseqslam")
PHASE1_SUMMARY = os.path.join(ROOT, "SEQ_SLAM/reports/oxford/Phase1_summary.csv")
OUT_AUDIT = os.path.join(ROOT, "SEQ_SLAM/reports/oxford/Phase1_quality_audit.csv")
OUT_TRUSTED = os.path.join(ROOT, "SEQ_SLAM/reports/oxford/Phase1_summary_trusted.csv")

MIN_CORE_CORR = 0.70
MAX_NORM_MAE = 0.12
MIN_VALID_RATIO = 0.80


@dataclass
class PairConfig:
    reference_run: str
    query_run: str
    best_ds: int
    best_vmin: float
    best_vmax: float
    best_rwindow: int
    best_threshold: float
    rank_score: float
    valid_ratio: float
    core_corr: float
    norm_mae: float
    result_dir: str
    raw_row: dict


def _f(value: str, default: float = float("nan")) -> float:
    try:
        return float(value)
    except Exception:
        return default


def load_phase1_configs() -> List[PairConfig]:
    configs: List[PairConfig] = []
    with open(PHASE1_SUMMARY, newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            configs.append(
                PairConfig(
                    reference_run=row["reference_run"],
                    query_run=row["query_run"],
                    best_ds=int(_f(row["best_ds"], 0)),
                    best_vmin=_f(row["best_vmin"]),
                    best_vmax=_f(row["best_vmax"]),
                    best_rwindow=int(_f(row["best_rwindow"], 0)),
                    best_threshold=_f(row["best_threshold"]),
                    rank_score=_f(row["rank_score"]),
                    valid_ratio=_f(row["valid_ratio"]),
                    core_corr=_f(row["core_corr"]),
                    norm_mae=_f(row["norm_mae"]),
                    result_dir=os.path.join(ROOT, row["result_dir"]),
                    raw_row=row,
                )
            )
    return configs


def regenerate_plot_for_pair(cfg: PairConfig) -> None:
    params, _, _, _, _, _, _ = _prepare_params(
        cfg.reference_run,
        cfg.query_run,
        use_cache=True,
        query_stride=1,
        auto_query_stride=True,
    )
    params.DO_FIND_MATCHES = 0

    ss = SeqSLAM(params)
    try:
        results = ss.run()
    except AttributeError as exc:
        if "results_preprocessing" not in str(exc):
            raise
        params.dataset[0].preprocessing.load = 0
        params.dataset[1].preprocessing.load = 0
        params.differenceMatrix.load = 0
        params.contrastEnhanced.load = 0
        ss = SeqSLAM(params)
        results = ss.run()
    dd = results.DD
    n_ref, n_query = dd.shape

    ss.params.matching.ds = cfg.best_ds
    ss.params.matching.Rwindow = cfg.best_rwindow
    ss.params.matching.vmin = cfg.best_vmin
    ss.params.matching.vmax = cfg.best_vmax

    best_matches = ss.getMatches(dd)

    os.makedirs(cfg.result_dir, exist_ok=True)
    out_plot = os.path.join(cfg.result_dir, "oxford_tuning_best_matchings.png")
    title = (
        "Best tuned matching "
        f"(ds={cfg.best_ds}, v=({cfg.best_vmin:.2f},{cfg.best_vmax:.2f}), "
        f"Rwindow={cfg.best_rwindow}, thresh={cfg.best_threshold:.2f}, "
        f"valid={int(round(cfg.valid_ratio * n_query))}/{n_query})"
    )
    _plot_matches(
        best_matches,
        threshold=cfg.best_threshold,
        save_path=out_plot,
        title=title,
        n_ref=n_ref,
    )


def classify(cfg: PairConfig) -> Tuple[str, str]:
    reasons = []
    if cfg.core_corr < MIN_CORE_CORR:
        reasons.append("core_corr_below_threshold")
    if cfg.norm_mae > MAX_NORM_MAE:
        reasons.append("norm_mae_above_threshold")
    if cfg.valid_ratio < MIN_VALID_RATIO:
        reasons.append("valid_ratio_below_threshold")

    if reasons:
        return "weak", "|".join(reasons)
    return "trusted", "passes_strict_gate"


def write_audit(configs: List[PairConfig]) -> List[dict]:
    rows = []
    for cfg in configs:
        status, reason = classify(cfg)
        rows.append(
            {
                "reference_run": cfg.reference_run,
                "query_run": cfg.query_run,
                "rank_score": cfg.rank_score,
                "valid_ratio": cfg.valid_ratio,
                "core_corr": cfg.core_corr,
                "norm_mae": cfg.norm_mae,
                "status": status,
                "reason": reason,
                "strict_gate": (
                    f"core_corr>={MIN_CORE_CORR},"
                    f"norm_mae<={MAX_NORM_MAE},"
                    f"valid_ratio>={MIN_VALID_RATIO}"
                ),
            }
        )

    with open(OUT_AUDIT, "w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "reference_run",
                "query_run",
                "rank_score",
                "valid_ratio",
                "core_corr",
                "norm_mae",
                "status",
                "reason",
                "strict_gate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def write_trusted_summary(configs: List[PairConfig], audit_rows: List[dict]) -> None:
    trusted_keys = {
        (row["reference_run"], row["query_run"])
        for row in audit_rows
        if row["status"] == "trusted"
    }

    with open(PHASE1_SUMMARY, newline="") as src:
        reader = csv.DictReader(src)
        phase1_rows = list(reader)
        fieldnames = reader.fieldnames

    trusted_rows = [
        row
        for row in phase1_rows
        if (row["reference_run"], row["query_run"]) in trusted_keys
    ]

    with open(OUT_TRUSTED, "w", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(trusted_rows)


def main() -> None:
    os.chdir(PYSEQSLAM_DIR)
    configs = load_phase1_configs()
    print(f"Loaded {len(configs)} Phase-1 rows")

    for idx, cfg in enumerate(configs, start=1):
        print(f"[{idx}/{len(configs)}] regenerating plot: {cfg.reference_run} vs {cfg.query_run}")
        regenerate_plot_for_pair(cfg)

    audit_rows = write_audit(configs)
    write_trusted_summary(configs, audit_rows)

    trusted_count = sum(1 for r in audit_rows if r["status"] == "trusted")
    weak_count = len(audit_rows) - trusted_count
    print("Done.")
    print(f"Trusted: {trusted_count} | Weak: {weak_count}")
    print(f"Audit CSV: {OUT_AUDIT}")
    print(f"Trusted summary CSV: {OUT_TRUSTED}")


if __name__ == "__main__":
    main()
