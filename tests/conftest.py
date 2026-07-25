"""
####################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2026 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
####################################################################################
"""

import os

# Importing websiteapp pulls in Qt. Nothing here constructs a QApplication, but
# pinning the offscreen platform keeps the suite runnable over SSH and in CI, where
# there is no display.
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
