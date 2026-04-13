#!/bin/bash

# setup_mac.sh
# Automates the downloading and patching of ORB_SLAM3 for macOS Apple Silicon (M4)

set -e # Exit immediately if a command exits with a non-zero status

echo "--- Setting up ORB_SLAM3 for Apple Silicon ---"

# 1. Clone the repository if it doesn't exist
if [ ! -d "ORB_SLAM3" ]; then
    echo "Cloning ORB_SLAM3..."
    git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git
    # Remove the .git folder so it doesn't show up as a nested submodule in VS Code
    rm -rf ORB_SLAM3/.git
else
    echo "ORB_SLAM3 already exists. Please remove it or rename it to do a fresh install."
    exit 1
fi

echo "Patching CMakeLists.txt files for ARM and macOS..."

# 2. Patch CMakeLists.txt in ORB_SLAM3
# Replace -march=native with -DCMAKE_OSX_ARCHITECTURES=arm64
sed -i '' 's/-march=native/-DCMAKE_OSX_ARCHITECTURES=arm64/g' ORB_SLAM3/CMakeLists.txt
# Update C++ minimum standard to C++14
sed -i '' 's/-std=c++11/-std=c++14/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/-std=c++0x/-std=c++14/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/COMPILER_SUPPORTS_CXX11/COMPILER_SUPPORTS_CXX14/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/COMPILER_SUPPORTS_CXX0X/COMPILER_SUPPORTS_CXX14/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/DCOMPILEDWITHC11/DCOMPILEDWITHC14/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/DCOMPILEDWITHC0X/DCOMPILEDWITHC14/g' ORB_SLAM3/CMakeLists.txt
# Lower OpenCV requirement to 4.2
sed -i '' 's/find_package(OpenCV 4.4)/find_package(OpenCV 4.2)/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/OpenCV > 4.4 not found./OpenCV > 4.2 not found./g' ORB_SLAM3/CMakeLists.txt
# Change .so to .dylib for linked third-party libraries
sed -i '' 's/libDBoW2.so/libDBoW2.dylib/g' ORB_SLAM3/CMakeLists.txt
sed -i '' 's/libg2o.so/libg2o.dylib/g' ORB_SLAM3/CMakeLists.txt

# 3. Patch CMakeLists.txt in Thirdparty/DBoW2
sed -i '' 's/-march=native/-DCMAKE_OSX_ARCHITECTURES=arm64/g' ORB_SLAM3/Thirdparty/DBoW2/CMakeLists.txt

# 4. Patch CMakeLists.txt in Thirdparty/g2o
sed -i '' 's/-march=native/-DCMAKE_OSX_ARCHITECTURES=arm64/g' ORB_SLAM3/Thirdparty/g2o/CMakeLists.txt

# 5. Fix Eigen3 dependency issues
sed -i '' 's/FIND_PACKAGE(Eigen3 3.1.0 REQUIRED)/FIND_PACKAGE(Eigen3 REQUIRED)/gI' ORB_SLAM3/Thirdparty/g2o/CMakeLists.txt
sed -i '' 's/find_package(Eigen3 3.1.0 REQUIRED)/find_package(Eigen3 REQUIRED)/gI' ORB_SLAM3/CMakeLists.txt

# 6. Add homebrew include/lib paths to CMakeLists.txt
echo "include_directories(/opt/homebrew/include)" >> ORB_SLAM3/CMakeLists.txt
echo "include_directories(/opt/homebrew/include/eigen3)" >> ORB_SLAM3/CMakeLists.txt
echo "link_directories(/opt/homebrew/lib)" >> ORB_SLAM3/CMakeLists.txt
echo "include_directories(/opt/homebrew/include)" >> ORB_SLAM3/Thirdparty/DBoW2/CMakeLists.txt
echo "include_directories(/opt/homebrew/include/eigen3)" >> ORB_SLAM3/Thirdparty/g2o/CMakeLists.txt

# 7. Update CMake minimum requirements
find ORB_SLAM3 -name "CMakeLists.txt" -exec sed -i '' 's/cmake_minimum_required(VERSION 2.8)/cmake_minimum_required(VERSION 3.5)/gI' {} +
find ORB_SLAM3 -name "CMakeLists.txt" -exec sed -i '' 's/CMAKE_MINIMUM_REQUIRED(VERSION 2.6)/cmake_minimum_required(VERSION 3.5)/gI' {} +

echo "Patching source files..."

# 8. Fix missing unistd.h in source files
FILES_WITH_USLEEP=(
    "src/Viewer.cc" "src/System.cc" "src/LoopClosing.cc" "src/LocalMapping.cc" "src/Atlas.cc" "src/Tracking.cc"
)
for f in "${FILES_WITH_USLEEP[@]}"; do
    if [ -f "ORB_SLAM3/$f" ]; then
        # Check if already included to avoid double inclusion if run multiple times
        if ! grep -q "<unistd.h>" "ORB_SLAM3/$f"; then
            sed -i '' '1i\
#include <unistd.h>
' "ORB_SLAM3/$f"
        fi
    fi
done

# Find and patch usleep in all Examples and Examples_old
for f in $(find ORB_SLAM3/Examples ORB_SLAM3/Examples_old -name "*.cc"); do
    if ! grep -q "<unistd.h>" "$f"; then
        sed -i '' '1i\
#include <unistd.h>
' "$f"
    fi
done

# 9. Fix stdint-gcc.h
if [ -f "ORB_SLAM3/Thirdparty/DBoW2/DBoW2/FORB.cpp" ]; then
    sed -i '' 's/#include <stdint-gcc.h>/#include <stdint.h>/g' ORB_SLAM3/Thirdparty/DBoW2/DBoW2/FORB.cpp
fi
if [ -f "ORB_SLAM3/src/ORBmatcher.cc" ]; then
    sed -i '' 's/#include<stdint-gcc.h>/#include <stdint.h>/g' ORB_SLAM3/src/ORBmatcher.cc
fi

# 10. Fix tr1 namespace in g2o
find ORB_SLAM3/Thirdparty/g2o -type f -exec sed -i '' 's/tr1\/unordered_map/unordered_map/g' {} +
find ORB_SLAM3/Thirdparty/g2o -type f -exec sed -i '' 's/tr1\/memory/memory/g' {} +
find ORB_SLAM3/Thirdparty/g2o -type f -exec sed -i '' 's/std::tr1::/std::/g' {} +

# 11. Fix monotonic_clock in macOS std::chrono
find ORB_SLAM3/Examples ORB_SLAM3/Examples_old -name "*.cc" -exec sed -i '' 's/monotonic_clock/steady_clock/g' {} +

echo "--- Patching Complete ---"
echo "To build ORB_SLAM3, please run:"
echo "cd ORB_SLAM3 && chmod +x build.sh && ./build.sh"
