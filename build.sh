#!/bin/bash

ACTVATED=0
if [[ -n "{$VIRTUAL_ENV}" ]]; then
	source venv/bin/activate
	ACTIVATED=1
fi

python3 -m build &&
	pip uninstall --yes dist/website_as_app-1.0.0-py3-none-any.whl &&
	pip install dist/website_as_app-1.0.0-py3-none-any.whl

if [[ ${ACTIVATED} -eq 1 ]]; then
	deactivate
fi

