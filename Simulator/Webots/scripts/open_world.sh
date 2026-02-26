#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBOTS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_WORLD="${WEBOTS_DIR}/worlds/city/city.wbt"

WORLD_PATH="${1:-$DEFAULT_WORLD}"

if [[ ! -f "${WORLD_PATH}" ]]; then
  CANDIDATE="${WEBOTS_DIR}/worlds/${WORLD_PATH}"
  if [[ -f "${CANDIDATE}" ]]; then
    WORLD_PATH="${CANDIDATE}"
  else
    echo "World file not found: ${WORLD_PATH}" >&2
    echo "Usage: ${0} [absolute-world-path|relative-path-under-worlds]" >&2
    exit 1
  fi
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  MAC_WEBOTS_HOME="/Applications/Webots.app/Contents"
  MAC_WEBOTS_BIN="${MAC_WEBOTS_HOME}/MacOS/webots"

  if [[ ! -x "${MAC_WEBOTS_BIN}" ]]; then
    echo "Webots binary not found at ${MAC_WEBOTS_BIN}" >&2
    echo "Install Webots in /Applications or update this script." >&2
    exit 1
  fi

  if [[ -n "${WEBOTS_HOME:-}" && "${WEBOTS_HOME}" != "${MAC_WEBOTS_HOME}" ]]; then
    echo "Overriding WEBOTS_HOME='${WEBOTS_HOME}' -> '${MAC_WEBOTS_HOME}'"
  fi

  export WEBOTS_HOME="${MAC_WEBOTS_HOME}"
  exec "${MAC_WEBOTS_BIN}" "${WORLD_PATH}"
fi

# Non-macOS fallback.
if [[ -n "${WEBOTS_HOME:-}" ]]; then
  if [[ -x "${WEBOTS_HOME}/webots" ]]; then
    exec "${WEBOTS_HOME}/webots" "${WORLD_PATH}"
  fi
  if [[ -x "${WEBOTS_HOME}/bin/webots" ]]; then
    exec "${WEBOTS_HOME}/bin/webots" "${WORLD_PATH}"
  fi
fi

if command -v webots >/dev/null 2>&1; then
  exec webots "${WORLD_PATH}"
fi

echo "Unable to locate Webots executable." >&2
echo "Set WEBOTS_HOME or install Webots in PATH." >&2
exit 1
