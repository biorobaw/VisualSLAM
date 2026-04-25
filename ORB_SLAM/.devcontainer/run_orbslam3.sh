#!/bin/bash
# run_orbslam3.sh — Helper script to invoke ORB_SLAM3 binaries inside the dev container
#
# Usage examples:
#   ./run_orbslam3.sh mono_tum /workspace/settings.yaml /workspace/data/images
#   ./run_orbslam3.sh stereo_euroc /workspace/settings.yaml /workspace/data/sequence /workspace/data/timestamps.txt
#
# Environment:
#   ORB_SLAM3_ROOT  — path to ORB_SLAM3 install (default: /opt/ORB_SLAM3)
#   ORB_VOCAB       — path to ORBvoc.txt (default: $ORB_SLAM3_ROOT/Vocabulary/ORBvoc.txt)

set -euo pipefail

ORB_SLAM3_ROOT="${ORB_SLAM3_ROOT:-/opt/ORB_SLAM3}"
ORB_VOCAB="${ORB_VOCAB:-${ORB_SLAM3_ROOT}/Vocabulary/ORBvoc.txt}"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <binary_name> <settings_yaml> [additional args...]"
    echo ""
    echo "Available binaries:"
    echo "  Monocular:          mono_tum, mono_kitti, mono_euroc, mono_tum_vi"
    echo "  Stereo:             stereo_kitti, stereo_euroc, stereo_tum_vi"
    echo "  RGB-D:              rgbd_tum"
    echo "  Mono-Inertial:      mono_inertial_euroc, mono_inertial_tum_vi"
    echo "  Stereo-Inertial:    stereo_inertial_euroc, stereo_inertial_tum_vi"
    echo ""
    echo "Example:"
    echo "  $0 mono_tum /workspace/VisualSLAM/ORB_SLAM/configs/oxford.yaml /workspace/data/images"
    exit 1
fi

BINARY_NAME="$1"
shift

# Locate the binary in Examples subdirectories
BINARY_PATH=""
for subdir in Monocular Stereo RGB-D Monocular-Inertial Stereo-Inertial RGB-D-Inertial; do
    candidate="${ORB_SLAM3_ROOT}/Examples/${subdir}/${BINARY_NAME}"
    if [ -x "$candidate" ]; then
        BINARY_PATH="$candidate"
        break
    fi
done

if [ -z "$BINARY_PATH" ]; then
    echo "ERROR: Binary '${BINARY_NAME}' not found in ${ORB_SLAM3_ROOT}/Examples/"
    echo "Available binaries:"
    find "${ORB_SLAM3_ROOT}/Examples" -maxdepth 2 -type f -executable | sort
    exit 1
fi

echo "=== ORB_SLAM3 Runner ==="
echo "Binary:     ${BINARY_PATH}"
echo "Vocabulary:  ${ORB_VOCAB}"
echo "Arguments:   $@"
echo "========================"

# Run ORB_SLAM3 with the vocabulary file prepended to arguments
exec "${BINARY_PATH}" "${ORB_VOCAB}" "$@"
