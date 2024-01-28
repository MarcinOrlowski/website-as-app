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
"""

from typing import List


class Const(object):
    APP_NAME: str = 'Website As App'
    APP_PROJECT_NAME: str = 'website-as-app'
    APP_VERSION: str = '1.0.0'
    APP_URL: str = 'https://github.com/MarcinOrlowski/website-as-app/'
    APP_DESCRIPTION: str = 'Opens any web site as standalone desktop app.'
    APP_YEAR: int = 2024

    APP_DESCRIPTION: List[str] = [
        f'{APP_NAME} v{APP_VERSION} * Copyright 2023-{APP_YEAR} by Marcin Orlowski.',
        APP_DESCRIPTION,
        APP_URL,
    ]
