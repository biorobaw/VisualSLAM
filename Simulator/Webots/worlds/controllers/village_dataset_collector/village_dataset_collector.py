"""Collect village image sequences using a road-centered teleport path.

Outputs under:
  <repo>/SEQ_SLAM/datasets/village_sim/<run_name>/
    mono_left/
    mono_front/
    mono_side/
    poses.csv
"""

import argparse
import csv
import math
import re
import shutil
import sys
from pathlib import Path

from vehicle import Driver


VEHICLE_Z = 0.4

# Closed loop selected in village map:
# -1186 -> -1302 -> -1270 -> -1266 -> -1256 -> -1260 -> -1292 -> -1312 -> -94 -> -1186
LOOP_SEGMENTS = [
    ("-1186", "-1302", "-2018"),
    ("-1302", "-1270", "-2210"),
    ("-1270", "-1266", "-2042_2"),
    ("-1266", "-1256", "-2088_4"),
    ("-1256", "-1260", "-2088_2"),
    ("-1260", "-1292", "-2092"),
    ("-1292", "-1312", "-2208"),
    ("-1312", "-94", "-1966"),
    ("-94", "-1186", "-1980_1"),
]


def _v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _v_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _v_mul(v, s):
    return (v[0] * s, v[1] * s)


def _v_len(v):
    return math.hypot(v[0], v[1])


def _v_unit(v):
    n = _v_len(v)
    if n < 1e-9:
        return (0.0, 0.0), 0.0
    return (v[0] / n, v[1] / n), n


def _sample_line_points(p0, p1, spacing_m):
    d = _v_sub(p1, p0)
    seg_len = _v_len(d)
    steps = max(1, int(math.ceil(seg_len / max(0.1, spacing_m))))
    points = []
    for j in range(1, steps + 1):
        t = j / float(steps)
        points.append((p0[0] + d[0] * t, p0[1] + d[1] * t))
    return points


def _bezier3(p0, p1, p2, p3, t):
    u = 1.0 - t
    uu = u * u
    tt = t * t
    uuu = uu * u
    ttt = tt * t
    return (
        (uuu * p0[0]) + (3.0 * uu * t * p1[0]) + (3.0 * u * tt * p2[0]) + (ttt * p3[0]),
        (uuu * p0[1]) + (3.0 * uu * t * p1[1]) + (3.0 * u * tt * p2[1]) + (ttt * p3[1]),
    )


def _sample_cubic_connector(p0, p3, tan0, tan3, spacing_m):
    d = _v_len(_v_sub(p3, p0))
    if d < 1e-6:
        return []

    handle = max(1.0, min(0.5 * d, 6.0))
    p1 = _v_add(p0, _v_mul(tan0, handle))
    p2 = _v_sub(p3, _v_mul(tan3, handle))

    # Control polygon length is a good approximation for sampling density.
    approx_len = (
        _v_len(_v_sub(p1, p0))
        + _v_len(_v_sub(p2, p1))
        + _v_len(_v_sub(p3, p2))
    )
    steps = max(2, int(math.ceil(approx_len / max(0.1, spacing_m))))

    points = []
    for j in range(1, steps + 1):
        t = j / float(steps)
        points.append(_bezier3(p0, p1, p2, p3, t))
    return points


def _start_tangent(points):
    for i in range(1, len(points)):
        u, n = _v_unit(_v_sub(points[i], points[0]))
        if n > 1e-6:
            return u
    return (1.0, 0.0)


def _end_tangent(points):
    for i in range(len(points) - 2, -1, -1):
        u, n = _v_unit(_v_sub(points[-1], points[i]))
        if n > 1e-6:
            return u
    return (1.0, 0.0)


def parse_args():
    parser = argparse.ArgumentParser(description="Collect village sequence dataset.")
    parser.add_argument("--run-name", default="village_day_centerline", help="Output run folder name.")
    parser.add_argument(
        "--dataset-root",
        default="SEQ_SLAM/datasets/village_sim",
        help="Dataset root relative to repository root.",
    )
    parser.add_argument("--spacing-m", type=float, default=2.0, help="Meters between teleported samples.")
    parser.add_argument(
        "--yaw-lookahead-m",
        type=float,
        default=4.0,
        help="Heading lookahead distance in meters for smoother turn orientation.",
    )
    parser.add_argument("--laps", type=int, default=1, help="Number of loop laps.")
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


def _read_world_path(driver: Driver, repo_root: Path) -> Path:
    try:
        world_path = driver.getWorldPath()
        if world_path:
            p = Path(world_path)
            if p.exists():
                return p
    except Exception:
        pass
    fallback = repo_root / "Simulator/Webots/worlds/village/village.wbt"
    if fallback.exists():
        return fallback
    raise RuntimeError("Unable to locate village world file for road parsing.")


def _parse_village_roads(world_path: Path):
    text = world_path.read_text()
    roads = {}
    block_re = re.compile(r"Road\s*\{([^{}]|\{[^{}]*\})*\}", re.S)

    for m in block_re.finditer(text):
        block = m.group(0)
        rid_m = re.search(r'\bid\s+"([^"]+)"', block)
        if not rid_m:
            continue
        rid = rid_m.group(1)

        start_m = re.search(r'\bstartJunction\s+"([^"]+)"', block)
        end_m = re.search(r'\bendJunction\s+"([^"]+)"', block)
        if not start_m or not end_m:
            continue

        trans_m = re.search(r"\btranslation\s+([-0-9.eE]+)\s+([-0-9.eE]+)\s+([-0-9.eE]+)", block)
        rot_m = re.search(r"\brotation\s+([-0-9.eE]+)\s+([-0-9.eE]+)\s+([-0-9.eE]+)\s+([-0-9.eE]+)", block)
        wp_m = re.search(r"\bwayPoints\s*\[(.*?)\]", block, re.S)
        if not trans_m or not wp_m:
            continue

        tx, ty = float(trans_m.group(1)), float(trans_m.group(2))
        angle = float(rot_m.group(4)) if rot_m else 0.0
        c, s = math.cos(angle), math.sin(angle)

        nums = [
            float(x)
            for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", wp_m.group(1))
        ]
        local_xy = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 3) if i + 1 < len(nums)]
        global_xy = []
        for x, y in local_xy:
            gx = x * c - y * s + tx
            gy = x * s + y * c + ty
            global_xy.append((gx, gy))

        roads[rid] = {
            "start": start_m.group(1),
            "end": end_m.group(1),
            "xy": global_xy,
        }

    return roads


def _build_centerline_xy(roads, spacing_m: float):
    segments_xy = []
    for start_id, end_id, road_id in LOOP_SEGMENTS:
        if road_id not in roads:
            raise RuntimeError(f"Road id '{road_id}' not found in world.")
        road = roads[road_id]
        points = road["xy"][:]
        if road["start"] == start_id and road["end"] == end_id:
            pass
        elif road["start"] == end_id and road["end"] == start_id:
            points.reverse()
        else:
            raise RuntimeError(
                f"Road {road_id} endpoints mismatch: ({road['start']}->{road['end']}) "
                f"vs expected ({start_id}->{end_id})."
            )
        segments_xy.append(points)

    # Connect road centerlines through crossroads with curved connectors.
    path = segments_xy[0][:]
    for i in range(1, len(segments_xy)):
        prev = segments_xy[i - 1]
        cur = segments_xy[i]
        gap = _v_len(_v_sub(cur[0], path[-1]))
        if gap > 1e-6:
            connector = _sample_cubic_connector(
                path[-1],
                cur[0],
                _end_tangent(prev),
                _start_tangent(cur),
                spacing_m,
            )
            path.extend(connector)
        if _v_len(_v_sub(path[-1], cur[0])) < 1e-6:
            path.extend(cur[1:])
        else:
            path.extend(cur)

    # Close loop with a curved connector.
    close_gap = _v_len(_v_sub(path[0], path[-1]))
    if close_gap > 1e-6:
        connector = _sample_cubic_connector(
            path[-1],
            path[0],
            _end_tangent(segments_xy[-1]),
            _start_tangent(segments_xy[0]),
            spacing_m,
        )
        path.extend(connector)

    uniform = [path[0]]
    for i in range(len(path) - 1):
        uniform.extend(_sample_line_points(path[i], path[i + 1], spacing_m))

    # Remove duplicate closure point if present.
    if len(uniform) > 2 and _v_len(_v_sub(uniform[-1], uniform[0])) < 1e-6:
        uniform.pop()
    return uniform


def _yaw_with_lookahead(points, i, lookahead_m):
    n = len(points)
    x, y = points[i]
    j = i
    remaining = max(0.0, lookahead_m)
    while remaining > 0.0:
        k = (j + 1) % n
        seg = _v_sub(points[k], points[j])
        seg_len = _v_len(seg)
        if seg_len > remaining and seg_len > 1e-9:
            t = remaining / seg_len
            tx = points[j][0] + seg[0] * t
            ty = points[j][1] + seg[1] * t
            return math.atan2(ty - y, tx - x)
        remaining -= seg_len
        j = k
        if j == i:
            break
    tx, ty = points[(i + 1) % n]
    return math.atan2(ty - y, tx - x)


def build_points(roads, spacing_m: float, laps: int, yaw_lookahead_m: float):
    base_xy = _build_centerline_xy(roads, spacing_m)
    if len(base_xy) < 2:
        raise RuntimeError("Insufficient sampled points for village path.")

    one_lap = []
    n = len(base_xy)
    for i in range(n):
        x, y = base_xy[i]
        yaw = _yaw_with_lookahead(base_xy, i, yaw_lookahead_m)
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
        print("village_dataset_collector: ERROR: supervisor access unavailable.")
        print("village_dataset_collector: set `supervisor TRUE` in the vehicle node.")
        while driver.step() != -1:
            pass
        return

    translation_field = self_node.getField("translation")
    rotation_field = self_node.getField("rotation")

    front_camera = driver.getDevice("camera")
    side_camera = driver.getDevice("side_camera")
    if front_camera is None:
        raise RuntimeError("Front camera device 'camera' not found.")

    front_camera.enable(timestep)
    if side_camera is not None:
        side_camera.enable(timestep)
    if args.side_capture_source == "side_camera" and args.camera_mode in ("both", "side") and side_camera is None:
        raise RuntimeError("Side camera requested, but device 'side_camera' not found.")

    driver.setSteeringAngle(0.0)
    driver.setCruisingSpeed(0.0)
    driver.setBrakeIntensity(1.0)

    repo_root = find_repo_root(Path(__file__))
    world_path = _read_world_path(driver, repo_root)
    roads = _parse_village_roads(world_path)

    run_dir = repo_root / args.dataset_root / args.run_name
    if run_dir.exists():
        if args.overwrite:
            shutil.rmtree(run_dir)
        else:
            raise RuntimeError(f"Run directory already exists: {run_dir} (use --overwrite)")

    mono_left_dir = run_dir / "mono_left"
    mono_front_dir = run_dir / "mono_front"
    mono_side_dir = run_dir / "mono_side"
    mono_left_dir.mkdir(parents=True, exist_ok=True)
    mono_front_dir.mkdir(parents=True, exist_ok=True)
    mono_side_dir.mkdir(parents=True, exist_ok=True)

    points = build_points(roads, args.spacing_m, args.laps, args.yaw_lookahead_m)
    if not points:
        raise RuntimeError("No sample points generated.")

    print(f"village_dataset_collector: run={args.run_name}")
    print(f"village_dataset_collector: output={run_dir}")
    print(
        f"village_dataset_collector: points={len(points)}, spacing={args.spacing_m}m, "
        f"laps={args.laps}, road_centerline=True"
    )
    print(f"village_dataset_collector: yaw_lookahead={args.yaw_lookahead_m}m, curved_connectors=True")
    print(f"village_dataset_collector: world={world_path}")
    print(f"village_dataset_collector: camera_mode={args.camera_mode}")
    print(
        f"village_dataset_collector: side_capture_source={args.side_capture_source}, "
        f"side_yaw_deg={args.side_yaw_deg}"
    )

    poses_path = run_dir / "poses.csv"
    frame_idx = 1
    max_frames = max(0, int(args.max_frames))

    with poses_path.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["frame_id", "x", "y", "yaw_rad"])

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

            if not set_pose_and_settle(x, y, yaw, args.settle_steps):
                return
            if args.camera_mode in ("both", "front"):
                front_camera.saveImage(str(mono_front_dir / filename), 100)
            if args.camera_mode == "front":
                front_camera.saveImage(str(mono_left_dir / filename), 100)

            if args.camera_mode in ("both", "side"):
                if args.side_capture_source == "rotate_car":
                    if not set_pose_and_settle(x, y, yaw + side_yaw_offset, args.side_settle_steps):
                        return
                    front_camera.saveImage(str(mono_side_dir / filename), 100)
                    front_camera.saveImage(str(mono_left_dir / filename), 100)
                else:
                    side_camera.saveImage(str(mono_side_dir / filename), 100)
                    side_camera.saveImage(str(mono_left_dir / filename), 100)

            writer.writerow([frame_idx, f"{x:.4f}", f"{y:.4f}", f"{yaw:.6f}"])
            frame_idx += 1

    print(f"village_dataset_collector: saved {frame_idx - 1} frames")
    print("village_dataset_collector: done")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"village_dataset_collector: ERROR: {exc}")
        sys.exit(1)
