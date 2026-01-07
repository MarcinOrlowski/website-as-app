"""
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
# @file      websiteapp/const.py
#
##################################################################################
"""

from typing import List

from websiteapp._version import __version__


class Const(object):
    APP_NAME: str = 'Website As App'
    APP_PROJECT_NAME: str = 'website-as-app'
    APP_VERSION: str = __version__
    APP_URL: str = 'https://github.com/MarcinOrlowski/website-as-app/'
    APP_DESCRIPTION: str = 'Opens any web site as standalone desktop app.'
    APP_YEAR: int = 2026

    APP_DESCRIPTION: List[str] = [
        f'{APP_NAME} v{APP_VERSION} * Copyright 2023-{APP_YEAR} by Marcin Orlowski.',
        APP_DESCRIPTION,
        APP_URL,
    ]

    # Set Chrome-like user agent
    __chrome_version = "115.0.5790.170"  # Using a recent stable Chrome version
    __webkit_version = "537.36"  # WebKit version used by Chrome
    APP_USER_AGENT = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{__webkit_version} (KHTML, like Gecko) Chrome/{__chrome_version} Safari/{__webkit_version}"
