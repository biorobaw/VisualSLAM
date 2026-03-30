#!/usr/bin/env python3
"""Convert simulator poses.csv (frame_id,x,y,yaw_rad) to TUM trajectory format.

Output line format:
    timestamp tx ty tz qx qy qz qw
"""

import argparse
import csv
import math
from pathlib import Path


def yaw_to_quaternion(yaw_rad: float):
    half = yaw_rad * 0.5
    qx = 0.0
    qy = 0.0
    qz = math.sin(half)
    qw = math.cos(half)
    return qx, qy, qz, qw


def convert(input_csv: Path, output_tum: Path, fps: float, use_frame_id_time: bool):
    with input_csv.open() as fp:
        reader = csv.DictReader(fp)
        required = {"frame_id", "x", "y", "yaw_rad"}
        fields = set(reader.fieldnames or [])
        if not required.issubset(fields):
            raise ValueError(f"Missing required columns. Expected {sorted(required)}, got {reader.fieldnames}")

        rows = list(reader)

    output_tum.parent.mkdir(parents=True, exist_ok=True)
    with output_tum.open("w") as out:
        for row in rows:
            frame_id = int(row["frame_id"])
            x = float(row["x"])
            y = float(row["y"])
            yaw = float(row["yaw_rad"])

            timestamp = float(frame_id) if use_frame_id_time else (float(frame_id - 1) / fps)
            tx, ty, tz = x, y, 0.0
            qx, qy, qz, qw = yaw_to_quaternion(yaw)

            out.write(
                f"{timestamp:.6f} {tx:.6f} {ty:.6f} {tz:.6f} {qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n"
            )

    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="Convert simulator poses.csv to TUM trajectory format")
    parser.add_argument("--input", required=True, help="Path to poses.csv")
    parser.add_argument("--output", required=True, help="Path to output .tum.txt")
    parser.add_argument("--fps", type=float, default=10.0, help="FPS used for timestamp synthesis when not using frame_id time")
    parser.add_argument(
        "--use-frame-id-time",
        action="store_true",
        help="Use frame_id as timestamp directly (seconds) instead of frame_id/fps",
    )
    args = parser.parse_args()

    count = convert(Path(args.input), Path(args.output), args.fps, args.use_frame_id_time)
    print(f"Converted {count} poses -> {args.output}")


if __name__ == "__main__":
    main()
