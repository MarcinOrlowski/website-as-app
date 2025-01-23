#!/bin/bash

##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2025 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
#####

set -uo pipefail

function runWebAppInVenv {
  readonly ROOT_DIR="$(dirname "$(realpath "${0}")")"
  readonly VENV_NAME="venv"
  readonly VENV_PATH="../venv/"

  pushd "${ROOT_DIR}" > /dev/null

  local ACTIVATED_VENV=
  if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    if [[ ! -d "${VENV_PATH}" ]]; then
      echo "Virtual env ${VENV_NAME} not found in ${VENV_PATH}"
      exit 100
    fi
    source "${VENV_PATH}/bin/activate"
    ACTIVATED_VENV="YES"
  fi

  webapp "$@"

  if [[ "${ACTIVATED_VENV:-}" == "YES" ]]; then
    deactivate
  fi

  popd > /dev/null
}

runWebAppInVenv "$@"
