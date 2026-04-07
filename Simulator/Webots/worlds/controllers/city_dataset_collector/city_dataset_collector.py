"""Collect city-world image sequences using teleport poses.

Outputs under:
  <repo>/<dataset_root>/<run_name>/
    mono_left/   (SeqSLAM primary stream)
    mono_right/
    mono_front/
    mono_side/   (legacy alias of mono_left)
    poses.csv
"""

import argparse
import csv
import math
import shutil
import sys
from pathlib import Path

from vehicle import Driver


VEHICLE_Z = 0.4


def _v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _v_len(v):
    return math.hypot(v[0], v[1])


def _sample_line_points(p0, p1, spacing_m):
    d = _v_sub(p1, p0)
    seg_len = _v_len(d)
    steps = max(1, int(math.ceil(seg_len / max(0.1, spacing_m))))
    pts = []
    for j in range(1, steps + 1):
        t = j / float(steps)
        pts.append((p0[0] + d[0] * t, p0[1] + d[1] * t))
    return pts


def _sample_arc_points(center, radius, start_angle, end_angle, spacing_m, ccw):
    a0 = start_angle
    a1 = end_angle
    if ccw:
        while a1 <= a0:
            a1 += 2.0 * math.pi
    else:
        while a1 >= a0:
            a1 -= 2.0 * math.pi

    delta = a1 - a0
    arc_len = abs(delta) * radius
    steps = max(1, int(math.ceil(arc_len / max(0.1, spacing_m))))
    pts = []
    for j in range(1, steps + 1):
        a = a0 + delta * (j / float(steps))
        pts.append((center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)))
    return pts


def _build_outer_loop_centerline_xy(spacing_m):
    # Built from city.wbt road primitives and intersection connectors:
    # 25->24->23->22->16->21->20->19->18->17->25
    segments = [
        ("line", (-105.0, 4.5), (-105.0, -64.5)),
        ("arc", (-64.5, -64.5), 40.5, math.pi, 1.5 * math.pi, True),      # road(2) reverse
        ("line", (-64.5, -105.0), (4.5, -105.0)),
        ("arc", (4.5, -64.5), 40.5, 1.5 * math.pi, 2.0 * math.pi, True),   # road(4) reverse
        ("arc", (64.5, -64.5), 19.5, math.pi, 0.5 * math.pi, False),       # intersection 16 connector
        ("arc", (64.5, -4.5), 40.5, 1.5 * math.pi, 2.0 * math.pi, True),   # road(11) reverse
        ("line", (105.0, -4.5), (105.0, 64.5)),
        ("arc", (64.5, 64.5), 40.5, 0.0, 0.5 * math.pi, True),             # road(13) reverse
        ("line", (64.5, 105.0), (-4.5, 105.0)),
        ("arc", (-4.5, 64.5), 40.5, 0.5 * math.pi, math.pi, True),         # road(15) reverse
        ("arc", (-64.5, 64.5), 19.5, 0.0, 1.5 * math.pi, False),            # intersection 17 connector
        ("arc", (-64.5, 4.5), 40.5, 0.5 * math.pi, math.pi, True),          # road(0) reverse
    ]

    points = [segments[0][1]]
    for seg in segments:
        if seg[0] == "line":
            _, p0, p1 = seg
            points.extend(_sample_line_points(p0, p1, spacing_m))
        else:
            _, center, radius, start_angle, end_angle, ccw = seg
            points.extend(_sample_arc_points(center, radius, start_angle, end_angle, spacing_m, ccw))

    if len(points) > 2 and _v_len(_v_sub(points[-1], points[0])) < 1e-6:
        points.pop()
    return points


def parse_args():
    parser = argparse.ArgumentParser(description="Collect city sequence dataset.")
    parser.add_argument("--run-name", default="city_day_outer_loop", help="Output run folder name.")
    parser.add_argument(
        "--dataset-root",
        default="SEQ_SLAM/datasets/oxford",
        help="Dataset root relative to repository root.",
    )
    parser.add_argument("--spacing-m", type=float, default=3.0, help="Meters between teleported samples.")
    parser.add_argument("--laps", type=int, default=1, help="Number of loop laps.")
    parser.add_argument(
        "--corner-radius-m",
        type=float,
        default=25.0,
        help="Deprecated compatibility arg. Ignored in road-centerline mode.",
    )
    parser.add_argument("--settle-steps", type=int, default=3, help="Steps to wait after teleport before saving.")
    parser.add_argument(
        "--camera-mode",
        choices=["both", "front", "side"],
        default="both",
        help="Which camera streams to save.",
    )
    parser.add_argument(
        "--side-capture-source",
        choices=["rotate_car", "side_camera"],
        default="rotate_car",
        help="How to get side images: rotate car heading or use side camera device.",
    )
    parser.add_argument(
        "--side-yaw-deg",
        type=float,
        default=90.0,
        help="Side-view yaw offset in degrees when using --side-capture-source rotate_car.",
    )
    parser.add_argument(
        "--side-settle-steps",
        type=int,
        default=2,
        help="Steps to wait after yaw-rotating for side capture.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
        help="Optional hard cap on frames (0 = no limit).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing run directory if it exists.",
    )
    args, _ = parser.parse_known_args()
    return args


def find_repo_root(start_path: Path) -> Path:
    p = start_path.resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "SEQ_SLAM").is_dir() and (candidate / "Simulator").is_dir():
            return candidate
    raise RuntimeError("Could not locate repository root from controller path.")


def build_smooth_points(spacing_m: float, laps: int):
    base_xy = _build_outer_loop_centerline_xy(spacing_m)
    if len(base_xy) < 2:
        raise RuntimeError("Insufficient sampled points for path.")

    one_lap = []
    n = len(base_xy)
    for i in range(n):
        x, y = base_xy[i]
        nx, ny = base_xy[(i + 1) % n]
        yaw = math.atan2(ny - y, nx - x)
        one_lap.append((x, y, yaw))

    points = []
    for _ in range(max(1, laps)):
        points.extend(one_lap)
    return points


def main():
    args = parse_args()

    driver = Driver()
    timestep = int(driver.getBasicTimeStep())

    self_node = driver.getSelf()
    if self_node is None:
        print("city_dataset_collector: ERROR: supervisor access unavailable.")
        print("city_dataset_collector: set `supervisor TRUE` in the BmwX5 node.")
        while driver.step() != -1:
            pass
        return

    translation_field = self_node.getField("translation")
    rotation_field = self_node.getField("rotation")

    front_camera = driver.getDevice("camera")
    side_camera = driver.getDevice("side_camera")
    right_camera = driver.getDevice("right_camera")
    if front_camera is None:
        raise RuntimeError("Front camera device 'camera' not found.")

    front_camera.enable(timestep)
    if side_camera is not None:
        side_camera.enable(timestep)
    if right_camera is not None:
        right_camera.enable(timestep)
    if args.side_capture_source == "side_camera" and args.camera_mode in ("both", "side"):
        if side_camera is None:
            raise RuntimeError("Left side camera requested, but device 'side_camera' not found.")
        if right_camera is None:
            raise RuntimeError("Right side camera requested, but device 'right_camera' not found.")

    driver.setSteeringAngle(0.0)
    driver.setCruisingSpeed(0.0)
    driver.setBrakeIntensity(1.0)

    repo_root = find_repo_root(Path(__file__))
    run_dir = repo_root / args.dataset_root / args.run_name
    if run_dir.exists():
        if args.overwrite:
            shutil.rmtree(run_dir)
        else:
            raise RuntimeError(f"Run directory already exists: {run_dir} (use --overwrite)")

    mono_left_dir = run_dir / "mono_left"
    mono_right_dir = run_dir / "mono_right"
    mono_front_dir = run_dir / "mono_front"
    mono_side_dir = run_dir / "mono_side"
    mono_left_dir.mkdir(parents=True, exist_ok=True)
    mono_right_dir.mkdir(parents=True, exist_ok=True)
    mono_front_dir.mkdir(parents=True, exist_ok=True)
    mono_side_dir.mkdir(parents=True, exist_ok=True)

    points = build_smooth_points(args.spacing_m, args.laps)
    if not points:
        raise RuntimeError("No sample points generated.")

    print(f"city_dataset_collector: run={args.run_name}")
    print(f"city_dataset_collector: output={run_dir}")
    print(
        f"city_dataset_collector: points={len(points)}, spacing={args.spacing_m}m, "
        f"laps={args.laps}, road_centerline=True"
    )
    print(f"city_dataset_collector: camera_mode={args.camera_mode}")
    print(
        f"city_dataset_collector: side_capture_source={args.side_capture_source}, "
        f"side_yaw_deg={args.side_yaw_deg}"
    )

    poses_path = run_dir / "poses.csv"
    frame_idx = 1
    max_frames = max(0, int(args.max_frames))

    with poses_path.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["frame_id", "x", "y", "yaw_rad"])

        # Warm up sensors.
        for _ in range(3):
            if driver.step() == -1:
                return

        def set_pose_and_settle(px, py, pyaw, settle_steps):
            translation_field.setSFVec3f([px, py, VEHICLE_Z])
            rotation_field.setSFRotation([0, 0, 1, pyaw])
            self_node.resetPhysics()
            for _ in range(max(1, settle_steps)):
                if driver.step() == -1:
                    return False
            return True

        side_yaw_offset = math.radians(args.side_yaw_deg)

        for x, y, yaw in points:
            if max_frames and frame_idx > max_frames:
                break

            filename = f"{frame_idx:05d}.png"

            # Capture forward image first at path heading.
            if not set_pose_and_settle(x, y, yaw, args.settle_steps):
                return
            if args.camera_mode in ("both", "front"):
                front_camera.saveImage(str(mono_front_dir / filename), 100)
            if args.camera_mode == "front":
                front_camera.saveImage(str(mono_left_dir / filename), 100)

            # Capture left/right views either by rotating the vehicle heading or by
            # using dedicated side cameras when present in the world.
            if args.camera_mode in ("both", "side"):
                if args.side_capture_source == "rotate_car":
                    if not set_pose_and_settle(x, y, yaw + side_yaw_offset, args.side_settle_steps):
                        return
                    front_camera.saveImage(str(mono_left_dir / filename), 100)
                    front_camera.saveImage(str(mono_side_dir / filename), 100)
                    if not set_pose_and_settle(x, y, yaw - side_yaw_offset, args.side_settle_steps):
                        return
                    front_camera.saveImage(str(mono_right_dir / filename), 100)
                else:
                    side_camera.saveImage(str(mono_left_dir / filename), 100)
                    side_camera.saveImage(str(mono_side_dir / filename), 100)
                    right_camera.saveImage(str(mono_right_dir / filename), 100)

            writer.writerow([frame_idx, f"{x:.4f}", f"{y:.4f}", f"{yaw:.6f}"])
            frame_idx += 1

    print(f"city_dataset_collector: saved {frame_idx - 1} frames")
    print("city_dataset_collector: done")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"city_dataset_collector: ERROR: {exc}")
        sys.exit(1)
