# ORB_SLAM3 Dev Container — x86_64 Ubuntu 20.04
# Runs under Rosetta 2 emulation on Apple Silicon Macs
# Provides a reference-platform build with no macOS patches needed

FROM --platform=linux/amd64 ubuntu:20.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# ============================================================
# 1. System dependencies
# ============================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    pkg-config \
    # OpenCV dependencies
    libopencv-dev \
    # Eigen3
    libeigen3-dev \
    # Pangolin dependencies
    libglew-dev \
    libepoxy-dev \
    libgl1-mesa-dev \
    libwayland-dev \
    libxkbcommon-dev \
    wayland-protocols \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    # Boost (serialization required by ORB_SLAM3)
    libboost-serialization-dev \
    # OpenSSL (crypto required by ORB_SLAM3)
    libssl-dev \
    # Python (for evo evaluation tools)
    python3 \
    python3-dev \
    python3-pip \
    python3-numpy \
    # Useful utilities
    vim \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# 2. Build Pangolin from source
# ============================================================
WORKDIR /opt
RUN git clone --branch v0.8 --depth 1 https://github.com/stevenlovegrove/Pangolin.git && \
    cd Pangolin && \
    mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_TESTS=OFF \
      -DBUILD_EXAMPLES=OFF && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd /opt && rm -rf Pangolin

# ============================================================
# 3. Clone and build ORB_SLAM3 (upstream, unpatched)
# ============================================================
WORKDIR /opt
RUN git clone --depth 1 https://github.com/UZ-SLAMLab/ORB_SLAM3.git && \
    cd ORB_SLAM3 && \
    # Relax OpenCV version requirement (4.2 is API-compatible; upstream tested with 3.2)
    sed -i 's/find_package(OpenCV 4.4)/find_package(OpenCV 4.2)/' CMakeLists.txt && \
    # Upgrade C++ standard to C++14 (required by Pangolin v0.8's sigslot headers)
    sed -i 's/c++11/c++14/g; s/c++0x/c++14/g' CMakeLists.txt && \
    # Disable Pangolin viewer in all example binaries (headless container has no display)
    find Examples Examples_old -name '*.cc' -exec \
      sed -i -E 's/(ORB_SLAM3::System\s+SLAM\([^,]+,[^,]+,[^,]+,)\s*true/\1 false/g' {} + && \
    chmod +x build.sh && \
    ./build.sh

# ============================================================
# 4. Install Python evaluation tools
# ============================================================
RUN pip3 install --no-cache-dir \
    "evo>=1.2.0" \
    "scipy>=1.7.0" \
    "matplotlib>=3.4.0" \
    "pandas>=1.3.0"

# ============================================================
# 5. Set up workspace
# ============================================================
# The project repo will be mounted at /workspace
WORKDIR /workspace

# Symlink ORB_SLAM3 binaries into a convenient location
ENV ORB_SLAM3_ROOT=/opt/ORB_SLAM3
ENV PATH="${ORB_SLAM3_ROOT}/Examples/Monocular:${ORB_SLAM3_ROOT}/Examples/Stereo:${ORB_SLAM3_ROOT}/Examples/RGB-D:${PATH}"

# Verify the build produced the shared library
RUN ls -la /opt/ORB_SLAM3/lib/libORB_SLAM3.so

CMD ["/bin/bash"]
