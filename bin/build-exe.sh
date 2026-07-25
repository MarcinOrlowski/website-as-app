#!/usr/bin/env bash
#
# created *.spec file:
#
# $ pyinstaller --name webapp --onefile --console websiteapp/webapp.py
# # tweaked the file for the project
# $ pyinstaller file.spec

# https://github.com/batonogov/docker-pyinstaller

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# Script lives in bin/, the spec file and the build output live in the project root.
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
readonly SCRIPT_DIR PROJECT_DIR

readonly SPEC_FILE="webapp.spec"
readonly IMAGE="batonogov/pyinstaller-windows:latest"

log_error() { printf '%s\n' "ERROR: ${1}" >&2; }

main() {
  cd "${PROJECT_DIR}"

  if ! command -v docker >/dev/null 2>&1; then
    log_error "docker not found in PATH"
    exit 1
  fi

  if [[ ! -f "${SPEC_FILE}" ]]; then
    log_error "Spec file not found: ${PROJECT_DIR}/${SPEC_FILE}"
    exit 1
  fi

  docker run \
    --volume "${PROJECT_DIR}:/src/" \
    --env SPECFILE="./${SPEC_FILE}" \
    "${IMAGE}"
}

main "$@"
