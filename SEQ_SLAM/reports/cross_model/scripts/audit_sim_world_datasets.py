#!/usr/bin/env python3
"""Audit canonical sim-world datasets for completeness and consistency."""

from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path


CAMERAS = ("mono_front", "mono_left", "mono_right", "mono_side")
CANONICAL_RUNS = (
    ("city", "city_summer"),
    ("city", "city_night"),
    ("village", "village_summer"),
    ("village", "village_winter"),
)
LEGACY_ROOTS = ("city_sim", "village_sim")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit canonical sim-world datasets.")
    parser.add_argument(
        "--datasets-root",
        type=Path,
        default=Path("SEQ_SLAM/datasets"),
        help="Datasets root relative to the repository root.",
    )
    return parser.parse_args()


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("not a valid PNG header")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def load_pose_frame_ids(poses_path: Path) -> list[int]:
    frame_ids: list[int] = []
    with poses_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["frame_id", "x", "y", "yaw_rad"]:
            raise ValueError(f"unexpected header {reader.fieldnames!r}")
        for row in reader:
            frame_ids.append(int(row["frame_id"]))
    return frame_ids


def expected_filenames(frame_ids: list[int]) -> list[str]:
    return [f"{frame_id:05d}.png" for frame_id in frame_ids]


def audit_run(run_dir: Path) -> list[str]:
    issues: list[str] = []
    poses_path = run_dir / "poses.csv"
    if not poses_path.exists():
        return [f"{run_dir}: missing poses.csv"]

    try:
        frame_ids = load_pose_frame_ids(poses_path)
    except Exception as exc:  # pragma: no cover - surfaced in CLI output
        return [f"{poses_path}: failed to parse ({exc})"]

    if not frame_ids:
        issues.append(f"{poses_path}: no pose rows")
        return issues

    expected_ids = list(range(1, len(frame_ids) + 1))
    if frame_ids != expected_ids:
        issues.append(
            f"{poses_path}: frame_id sequence is not contiguous 1..{len(frame_ids)}"
        )

    expected_names = expected_filenames(expected_ids)
    expected_count = len(frame_ids)

    for camera in CAMERAS:
        camera_dir = run_dir / camera
        if not camera_dir.exists():
            issues.append(f"{run_dir}: missing camera directory {camera}")
            continue

        pngs = sorted(path.name for path in camera_dir.glob("*.png"))
        if len(pngs) != expected_count:
            issues.append(
                f"{camera_dir}: expected {expected_count} PNGs, found {len(pngs)}"
            )
            continue

        if pngs != expected_names:
            issues.append(f"{camera_dir}: PNG names do not match poses.csv frame ids")
            continue

        for sample_name in pngs:
            sample_path = camera_dir / sample_name
            try:
                width, height = read_png_size(sample_path)
            except Exception as exc:  # pragma: no cover - surfaced in CLI output
                issues.append(f"{sample_path}: failed PNG validation ({exc})")
                continue
            if (width, height) != (640, 480):
                issues.append(
                    f"{sample_path}: expected 640x480, found {width}x{height}"
                )

    return issues


def find_legacy_artifacts(datasets_root: Path) -> list[str]:
    warnings: list[str] = []
    for legacy_root_name in LEGACY_ROOTS:
        legacy_root = datasets_root / legacy_root_name
        if not legacy_root.exists():
            continue
        entries = sorted(path for path in legacy_root.rglob("*") if path.is_file())
        if entries:
            if all(path.name == "groundtruth.tum" for path in entries):
                warnings.append(
                    f"{legacy_root}: contains {len(entries)} legacy groundtruth.tum compatibility files"
                )
            else:
                warnings.append(
                    f"{legacy_root}: contains {len(entries)} leftover files from legacy sim-world datasets"
                )
        else:
            warnings.append(f"{legacy_root}: legacy directory still exists but is empty")
    return warnings


def main() -> int:
    args = parse_args()
    datasets_root = args.datasets_root.resolve()

    failures: list[str] = []
    for group, run_name in CANONICAL_RUNS:
        run_dir = datasets_root / group / run_name
        if not run_dir.exists():
            failures.append(f"{run_dir}: canonical run directory is missing")
            continue
        failures.extend(audit_run(run_dir))

    warnings = find_legacy_artifacts(datasets_root)

    if failures:
        print("FAIL")
        for failure in failures:
            print(f" - {failure}")
    else:
        print("PASS")
        for group, run_name in CANONICAL_RUNS:
            print(f" - {group}/{run_name}: canonical dataset is complete and consistent")

    if warnings:
        print("WARNINGS")
        for warning in warnings:
            print(f" - {warning}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
