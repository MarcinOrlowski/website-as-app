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
# @file      websiteapp/const.py
#
##################################################################################
"""

from enum import Enum
from typing import List


class Version(Enum):
    MAJOR = 1
    MINOR = 6
    PATCH = 0

    @classmethod
    def as_string(cls) -> str:
        return f"{cls.MAJOR.value}.{cls.MINOR.value}.{cls.PATCH.value}"


class Const(object):
    APP_NAME: str = 'Website As App'
    APP_PROJECT_NAME: str = 'website-as-app'
    APP_VERSION: str = Version.as_string()
    APP_URL: str = 'https://github.com/MarcinOrlowski/website-as-app/'
    APP_DESCRIPTION: str = 'Opens any web site as standalone desktop app.'
    APP_YEAR: int = 2024

    APP_DESCRIPTION: List[str] = [
        f'{APP_NAME} v{APP_VERSION} * Copyright 2023-{APP_YEAR} by Marcin Orlowski.',
        APP_DESCRIPTION,
        APP_URL,
    ]
