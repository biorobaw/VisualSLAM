# ORB_SLAM3 Dev Container

## Why a Dev Container?

The native macOS/ARM build of ORB_SLAM3 requires [11 categories of patches](../setup_mac.sh) to compile on Apple Silicon. Several of these patches can affect numerical output:

| Patch | Risk |
|---|---|
| `-march=native` replaced with invalid `-D` flag | **Medium** — no architecture optimization, different float behavior |
| OpenCV 4.4 → 4.2 version requirement lowered | **Low-Medium** — different feature detection internals |
| Eigen3 version requirement removed | **Low** — potential numerical differences |

This dev container runs **unpatched upstream ORB_SLAM3** on its reference platform (Ubuntu 20.04, x86_64) via Docker + Rosetta 2 emulation, ensuring results match the published benchmarks.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with **Rosetta 2 emulation** enabled
  - Docker Desktop → Settings → General → ✅ "Use Rosetta for x86_64/amd64 emulation on Apple Silicon"
- VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Quick Start

### Option 1: VS Code Dev Container (Recommended)

1. Open the `VisualSLAM/ORB_SLAM/` folder in VS Code
2. Press `Cmd+Shift+P` → "Dev Containers: Reopen in Container"
3. Wait for the container to build (~10-20 min first time, cached after)
4. You're now inside the container with ORB_SLAM3 pre-built at `/opt/ORB_SLAM3`

### Option 2: Docker CLI

```bash
# Build the image
cd VisualSLAM/ORB_SLAM/.devcontainer
docker build --platform linux/amd64 -t orbslam3-dev -f Dockerfile ..

# Run interactively with workspace mounted
docker run --platform linux/amd64 -it \
  -v "$(cd ../.. && pwd)":/workspace \
  orbslam3-dev /bin/bash
```

## Usage Inside the Container

### Environment Variables

| Variable | Value | Description |
|---|---|---|
| `ORB_SLAM3_ROOT` | `/opt/ORB_SLAM3` | ORB_SLAM3 installation directory |
| `ORB_VOCAB` | `/opt/ORB_SLAM3/Vocabulary/ORBvoc.txt` | Path to ORB vocabulary file |

### Running ORB_SLAM3

Use the helper script:

```bash
# Monocular TUM-format dataset
./run_orbslam3.sh mono_tum /workspace/configs/settings.yaml /workspace/data/images

# Stereo EuRoC-format dataset
./run_orbslam3.sh stereo_euroc /workspace/configs/settings.yaml /workspace/data/sequence /workspace/data/timestamps.txt
```

Or call binaries directly:

```bash
/opt/ORB_SLAM3/Examples/Monocular/mono_tum \
  /opt/ORB_SLAM3/Vocabulary/ORBvoc.txt \
  /workspace/configs/settings.yaml \
  /workspace/data/images
```

### Running Evaluation

```bash
# evo is pre-installed
evo_ape tum groundtruth.tum estimated.tum --align --correct_scale
evo_rpe tum groundtruth.tum estimated.tum
```

## Performance Notes

- Runs at ~2-4x slower than native due to Rosetta 2 x86_64 emulation
- This is acceptable for offline dataset processing (not real-time)
- First build takes 10-20 minutes; subsequent container starts are instant

## File Structure

```
.devcontainer/
├── Dockerfile          # x86_64 Ubuntu 20.04 with ORB_SLAM3 + dependencies
├── devcontainer.json   # VS Code dev container configuration
├── run_orbslam3.sh     # Helper script for running ORB_SLAM3 binaries
└── README.md           # This file
```
