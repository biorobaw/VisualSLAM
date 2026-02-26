"""Teleport the village car through a fixed loop (no driving physics)."""

import math

from vehicle import Driver


# Selected closed loop on village crossroads:
# -1186 -> -1302 -> -1270 -> -1266 -> -1256 ->
# -1260 -> -1292 -> -1312 -> -94 -> -1186
LOOP_IDS = [
    "-1186",
    "-1302",
    "-1270",
    "-1266",
    "-1256",
    "-1260",
    "-1292",
    "-1312",
    "-94",
]

LOOP_WAYPOINTS = [
    (503.433, -582.999),  # -1186
    (316.504, -465.405),  # -1302
    (336.589, -291.942),  # -1270
    (255.874, -314.964),  # -1266
    (246.296, -304.560),  # -1256
    (235.935, -314.183),  # -1260
    (79.882, -463.345),   # -1292
    (231.715, -599.539),  # -1312
    (516.884, -696.643),  # -94
]

VEHICLE_Z = 0.4
TELEPORT_INTERVAL_S = 2.0


driver = Driver()
self_node = driver.getSelf()

if self_node is None:
    print("village_loop_driver: ERROR: supervisor access unavailable.")
    print("village_loop_driver: set `supervisor TRUE` in the vehicle node.")
    while driver.step() != -1:
        pass
    raise SystemExit(1)

timestep = int(driver.getBasicTimeStep())
teleport_interval_steps = max(1, int(round((TELEPORT_INTERVAL_S * 1000.0) / max(1, timestep))))

translation_field = self_node.getField("translation")
rotation_field = self_node.getField("rotation")

driver.setSteeringAngle(0.0)
driver.setCruisingSpeed(0.0)
driver.setBrakeIntensity(1.0)


def teleport_to_waypoint(index):
    x, y = LOOP_WAYPOINTS[index]
    nx, ny = LOOP_WAYPOINTS[(index + 1) % len(LOOP_WAYPOINTS)]
    yaw = math.atan2(ny - y, nx - x)
    translation_field.setSFVec3f([x, y, VEHICLE_Z])
    rotation_field.setSFRotation([0, 0, 1, yaw])
    self_node.resetPhysics()
    print(f"village_loop_driver: teleport -> wp{index + 1}/{len(LOOP_WAYPOINTS)} id={LOOP_IDS[index]} ({x:.1f}, {y:.1f})")


print("village_loop_driver: loop -1186->-1302->-1270->-1266->-1256->-1260->-1292->-1312->-94->-1186")
print(f"village_loop_driver: interval={TELEPORT_INTERVAL_S:.1f}s ({teleport_interval_steps} steps)")

# Place at first waypoint immediately.
current_idx = 0
teleport_to_waypoint(current_idx)
current_idx = (current_idx + 1) % len(LOOP_WAYPOINTS)
steps_since_teleport = 0

while driver.step() != -1:
    driver.setCruisingSpeed(0.0)
    driver.setBrakeIntensity(1.0)
    driver.setSteeringAngle(0.0)

    steps_since_teleport += 1
    if steps_since_teleport >= teleport_interval_steps:
        teleport_to_waypoint(current_idx)
        current_idx = (current_idx + 1) % len(LOOP_WAYPOINTS)
        steps_since_teleport = 0
