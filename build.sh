#!/bin/bash

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

# Function to extract version from _version.py
extract_version() {
    sed -n 's/^__version__ *= *"\([^"]*\)".*/\1/p' "websiteapp/_version.py"
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
if [[ -z "${VIRTUAL_ENV}" ]]; then
    source venv/bin/activate
    ACTIVATED=1
fi

python3 -m build &&
    pip uninstall --yes "dist/website_as_app-${VERSION}-py3-none-any.whl" &&
    pip install "dist/website_as_app-${VERSION}-py3-none-any.whl"

if [[ ${ACTIVATED} -eq 1 ]]; then
    deactivate
fi
