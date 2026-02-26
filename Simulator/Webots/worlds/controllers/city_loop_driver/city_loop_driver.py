"""Teleport the city car along the true road centerline (no driving physics)."""

import math

from vehicle import Driver


# Outer loop (junction ids):
# 25 -> 24 -> 23 -> 22 -> 16 -> 21 -> 20 -> 19 -> 18 -> 17 -> 25
VEHICLE_Z = 0.4
SAMPLE_SPACING_M = 2.0
# city.wbt uses basicTimeStep=10ms, so 20 steps ~= 0.2s between teleports.
TELEPORT_INTERVAL_STEPS = 20


def _v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _v_len(v):
    return math.hypot(v[0], v[1])


def _sample_line_points(p0, p1, spacing_m):
    d = _v_sub(p1, p0)
    seg_len = _v_len(d)
    steps = max(1, int(math.ceil(seg_len / max(0.1, spacing_m))))
    points = []
    for j in range(1, steps + 1):
        t = j / float(steps)
        points.append((p0[0] + d[0] * t, p0[1] + d[1] * t))
    return points


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
    points = []
    for j in range(1, steps + 1):
        angle = a0 + delta * (j / float(steps))
        points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
    return points


def _build_outer_loop_centerline_xy(spacing_m):
    # Built from city.wbt road primitives and intersection connectors:
    # 25->24->23->22->16->21->20->19->18->17->25
    segments = [
        ("line", (-105.0, 4.5), (-105.0, -64.5)),
        ("arc", (-64.5, -64.5), 40.5, math.pi, 1.5 * math.pi, True),   # road(2) reverse
        ("line", (-64.5, -105.0), (4.5, -105.0)),
        ("arc", (4.5, -64.5), 40.5, 1.5 * math.pi, 2.0 * math.pi, True),  # road(4) reverse
        ("arc", (64.5, -64.5), 19.5, math.pi, 0.5 * math.pi, False),    # intersection 16 connector
        ("arc", (64.5, -4.5), 40.5, 1.5 * math.pi, 2.0 * math.pi, True),   # road(11) reverse
        ("line", (105.0, -4.5), (105.0, 64.5)),
        ("arc", (64.5, 64.5), 40.5, 0.0, 0.5 * math.pi, True),          # road(13) reverse
        ("line", (64.5, 105.0), (-4.5, 105.0)),
        ("arc", (-4.5, 64.5), 40.5, 0.5 * math.pi, math.pi, True),      # road(15) reverse
        ("arc", (-64.5, 64.5), 19.5, 0.0, 1.5 * math.pi, False),         # intersection 17 connector
        ("arc", (-64.5, 4.5), 40.5, 0.5 * math.pi, math.pi, True),       # road(0) reverse
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


def build_smooth_poses(spacing_m):
    points = _build_outer_loop_centerline_xy(spacing_m)
    if len(points) < 2:
        raise RuntimeError("Insufficient sampled path points.")

    poses = []
    n = len(points)
    for i in range(n):
        x, y = points[i]
        nx, ny = points[(i + 1) % n]
        yaw = math.atan2(ny - y, nx - x)
        poses.append((x, y, yaw))
    return poses


driver = Driver()
self_node = driver.getSelf()

if self_node is None:
    print("city_loop_driver: ERROR: supervisor access unavailable.")
    print("city_loop_driver: set `supervisor TRUE` in the BmwX5 node.")
    while driver.step() != -1:
        pass
    raise SystemExit(1)

translation_field = self_node.getField("translation")
rotation_field = self_node.getField("rotation")

driver.setSteeringAngle(0.0)
driver.setCruisingSpeed(0.0)
driver.setBrakeIntensity(1.0)

POSES = build_smooth_poses(SAMPLE_SPACING_M)


def teleport_to_pose(index):
    x, y, yaw = POSES[index]
    translation_field.setSFVec3f([x, y, VEHICLE_Z])
    rotation_field.setSFRotation([0, 0, 1, yaw])
    self_node.resetPhysics()
    if index % 25 == 0:
        print(f"city_loop_driver: teleport -> p{index + 1}/{len(POSES)} ({x:.1f}, {y:.1f})")


print("city_loop_driver: smooth outer loop 25->24->23->22->16->21->20->19->18->17->25")
print(
    f"city_loop_driver: points={len(POSES)} spacing={SAMPLE_SPACING_M}m "
    f"interval={TELEPORT_INTERVAL_STEPS * 0.01:.2f}s (road-centerline mode)"
)

current_idx = 0
steps_since_teleport = 0

while driver.step() != -1:
    driver.setCruisingSpeed(0.0)
    driver.setBrakeIntensity(1.0)
    driver.setSteeringAngle(0.0)

    steps_since_teleport += 1
    if steps_since_teleport >= TELEPORT_INTERVAL_STEPS:
        teleport_to_pose(current_idx)
        current_idx = (current_idx + 1) % len(POSES)
        steps_since_teleport = 0
