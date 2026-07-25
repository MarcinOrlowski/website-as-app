#!/usr/bin/env bash

##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2026 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
##################################################################################

set -euo pipefail

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# Script lives in bin/, everything it touches is relative to the project root.
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
readonly SCRIPT_NAME SCRIPT_DIR PROJECT_DIR

readonly PACKAGE_NAME="website-as-app"
readonly WHEEL_PREFIX="website_as_app"
readonly VERSION_FILE="websiteapp/_version.py"
readonly VENV_DIRS=("venv" ".venv")
readonly DIST_DIR="dist"

log_info() { printf '%s\n' "${1}"; }
log_error() { printf '%s\n' "ERROR: ${1}" >&2; }

show_usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Builds the wheel from the current sources, then reinstalls it into the
active virtual environment, or into the local "${VENV_DIRS[0]}/" ("${VENV_DIRS[1]}/") one.

  -n    Build only, skip uninstall/install step
  -h    Show this help
EOF
}

# Prints version literal from _version.py, or nothing when not found.
extract_version() {
  sed -n 's/^__version__ *= *"\([^"]*\)".*/\1/p' "${VERSION_FILE}"
}

ACTIVATED_VENV=0

# Deactivates venv only if this script activated it.
cleanup() {
  if [[ "${ACTIVATED_VENV}" -eq 1 ]]; then
    deactivate
  fi
}

main() {
  local build_only=0

  while getopts ":hn" opt; do
    case "${opt}" in
      h)
        show_usage
        exit 0
        ;;
      n) build_only=1 ;;
      \?)
        log_error "Unknown option: -${OPTARG}"
        exit 2
        ;;
    esac
  done
  shift $((OPTIND - 1))

  cd "${PROJECT_DIR}"

  if [[ ! -f "${VERSION_FILE}" ]]; then
    log_error "Version file not found: ${VERSION_FILE}"
    exit 1
  fi

  local version
  version="$(extract_version)"
  if [[ -z "${version}" ]]; then
    log_error "Failed to extract version from ${VERSION_FILE}"
    exit 1
  fi
  log_info "Current version: ${version}"

  if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    local activate=""
    local candidate
    for candidate in "${VENV_DIRS[@]}"; do
      if [[ -f "${candidate}/bin/activate" ]]; then
        activate="${candidate}/bin/activate"
        break
      fi
    done

    if [[ -z "${activate}" ]]; then
      log_error "No virtual env found in ${PROJECT_DIR} (looked for: ${VENV_DIRS[*]})"
      exit 1
    fi

    # shellcheck disable=SC1090,SC1091  # generated at venv creation time, not in repo
    source "${activate}"
    ACTIVATED_VENV=1
    trap cleanup EXIT
    log_info "Activated venv: ${activate%/bin/activate}"
  fi

  if ! python3 -c 'import build' >/dev/null 2>&1; then
    log_error "Python 'build' module not installed. Run: pip install -r requirements-dev.txt"
    exit 1
  fi

  python3 -m build

  local wheel="${DIST_DIR}/${WHEEL_PREFIX}-${version}-py3-none-any.whl"
  if [[ ! -f "${wheel}" ]]; then
    log_error "Built wheel not found: ${wheel}"
    exit 1
  fi

  if [[ "${build_only}" -eq 1 ]]; then
    log_info "Build only mode, skipping install of ${wheel}"
    return 0
  fi

  # Uninstall by package name, not by wheel path, so a stale/mismatched
  # version gets removed too. pip exits 0 when nothing is installed.
  pip uninstall --yes "${PACKAGE_NAME}"
  pip install "${wheel}"

  log_info "Installed ${PACKAGE_NAME} ${version}"
}

main "$@"
