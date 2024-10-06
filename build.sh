#!/bin/bash

##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2024 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
##################################################################################

# Function to extract version components from const.py
extract_version() {
    local const_file="websiteapp/const.py"
    local major=$(sed -n 's/.*MAJOR *= *\([0-9]\+\).*/\1/p' "$const_file")
    local minor=$(sed -n 's/.*MINOR *= *\([0-9]\+\).*/\1/p' "$const_file")
    local patch=$(sed -n 's/.*PATCH *= *\([0-9]\+\).*/\1/p' "$const_file")
    echo "${major}.${minor}.${patch}"
}

# Extract version
VERSION=$(extract_version)
echo "Current version: ${VERSION}"

# Check if version was successfully extracted
if [ -z "$VERSION" ]; then
    echo "Error: Failed to extract version from const source file."
    exit 1
fi

ACTIVATED=0
if [[ -n "${VIRTUAL_ENV}" ]]; then
    source venv/bin/activate
    ACTIVATED=1
fi

python3 -m build &&
    pip uninstall --yes "dist/website_as_app-${VERSION}-py3-none-any.whl" &&
    pip install "dist/website_as_app-${VERSION}-py3-none-any.whl"

if [[ ${ACTIVATED} -eq 1 ]]; then
    deactivate
fi
