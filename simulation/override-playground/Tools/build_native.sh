#!/bin/zsh
set -e
base="$(cd "$(dirname "$0")/.." && pwd)"
MJ="$base/.venv/lib/python3.11/site-packages/mujoco"
lib="$MJ/libmujoco.3.13.0.dylib"
clang -dynamiclib -arch arm64 -O3 -I "$MJ/include" "$base/Tools/bridge.c" "$lib" -Wl,-rpath,@loader_path -o "$base/Unity/Assets/Plugins/liboverride.dylib"
cp "$lib" "$base/Unity/Assets/Plugins/libmujoco.3.13.0.dylib"
install_name_tool -change @rpath/mujoco.framework/Versions/A/libmujoco.3.13.0.dylib @loader_path/libmujoco.3.13.0.dylib "$base/Unity/Assets/Plugins/liboverride.dylib"
codesign -f -s - "$base/Unity/Assets/Plugins/libmujoco.3.13.0.dylib"
codesign -f -s - "$base/Unity/Assets/Plugins/liboverride.dylib"
