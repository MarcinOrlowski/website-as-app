#!/usr/bin/env python3

"""
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
#####
#
# https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html
#
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements-dev.txt
# python -m build
# # Reinstall the app (do not do "install --upgrade" as cached bytecode can not be updated)
# pip uninstall --yes dist/website_as_app-1.0.0-py3-none-any.whl
# # intentionally no --upgrade for install to endforce conflict if not uninstalled fully first.
# pip install dist/website_as_app-1.0.0-py3-none-any.whl
# twine upload dist/*
#
"""

from setuptools import setup, find_packages

from websiteapp.const import Const

with open('README.md', 'r') as fh:
    readme = fh.read()

setup(
    name=Const.APP_PROJECT_NAME,
    version=Const.APP_VERSION,
    packages=find_packages(),

    install_requires=[
        'argparse>=1.4.0',
        'PySide6',
        'PyQtWebEngine',
    ],
    entry_points={
        'console_scripts': [
            'webapp = websiteapp.webapp:WebApp.run',
            'runasapp = websiteapp.webapp:WebApp.run',
        ],
    },

    package_data={
        'websiteapp': [
            'icons/default.png',
            'icons/logo.png',
        ],
    },

    author='Marcin Orlowski',
    author_email='mail@marcinOrlowski.com',
    description=Const.APP_DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/markdown',
    url=Const.APP_URL,
    keywords='webapp desktop app',
    project_urls={
        'Bug Tracker': f'{Const.APP_URL}/issues/',
        'Documentation': Const.APP_URL,
        'Source Code': Const.APP_URL,
    },
    # https://choosealicense.com/
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
