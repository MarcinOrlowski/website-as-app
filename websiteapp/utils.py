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
# @file      websiteapp/utils.py
#
##################################################################################
"""
import argparse
import importlib.resources as pkg_resources
import os
import re
from typing import Optional

from PySide6.QtGui import QIcon


class Utils(object):
    @staticmethod
    def get_icon(icon: Optional[str] = None) -> QIcon:
        """
        Attempts to construct QIcon object from given icon file path. If icon file is not given
        or does not exist, default icon is used (so it always return valid QIcon object).

        :param icon: Path to icon file (in format supported by QT, i.e. PNG)
        :return: QIcon object
        """
        icon_file = None

        if icon and os.path.exists(icon):
            icon_file = icon

        if icon_file is None:
            with pkg_resources.path('websiteapp.icons', 'default.png') as icon_path:
                icon_file = str(icon_path)

        return QIcon(icon_file)

    @staticmethod
    def parse_geometry(geometry_string: str) -> (int, int, int, int):
        """
        Parse the geometry string and return the width, height, x, and y values.

        :param geometry_string: A string representing the geometry in the format WIDTHxHEIGHT+X+Y.

        :return: A tuple containing the x, y,  width and height values.
        :raises ValueError: If the geometry string format is incorrect.
        """
        match = re.search(r'^(\d+)x(\d+)\+(\d+)\+(\d+)$', geometry_string)
        if not match:
            raise ValueError(f"Invalid geometry. Expected WIDTHxHEIGHT+X+Y, got '{geometry_string}")

        width = int(match.group(1))
        if width < 1:
            raise ValueError(f"Invalid geometry. Width must be greater than 0, got '{width}'")
        height = int(match.group(2))
        if height < 1:
            raise ValueError(f"Invalid geometry. Height must be greater than 0, got '{height}'")
        x = int(match.group(3))
        if x < 0:
            raise ValueError(f"Invalid geometry. X must be greater than or equal to 0, got '{x}'")
        y = int(match.group(4))
        if y < 0:
            raise ValueError(f"Invalid geometry. Y must be greater than or equal to 0, got '{y}'")

        return x, y, width, height

    @staticmethod
    def handle_args():
        """
        Create an argument parser to handle command line arguments for opening a website in a
        standalone window.

        :return: The parsed command line arguments.
        """
        parser = argparse.ArgumentParser(
            description="Open any website in standalone window (like it's an app)")
        parser.add_argument('url', type=str, help='The URL to open')

        parser.add_argument('--profile', '-p', type=str, default='default',
                            help='Profile name (for cookies isolation etc). Default: "%(default)s"')

        # Can't use "title" as it is swallowed by QT and used for window title which cannot be later
        # changed. So we use "name" instead.
        parser.add_argument('--name', '-n', type=str, default=None,
                            help='Application name (shown as window title)')

        parser.add_argument('--icon', '-i', type=str, default=None,
                            help='Full path to PNG image file to be used as app icon')
        parser.add_argument('--geometry', '-g', type=str, default='450x600+0+0',
                            help='Initial window ("WIDTHxHEIGHT+X+Y"). Default: "%(default)s"')
        parser.add_argument('--zoom', '-z', type=float, default="1.0",
                            help='WebView scale. Default: %(default)s (no scale change).')
        parser.add_argument('--no-tray', '-t', action='store_true',
                            help='Disables docking app in system tray (closing window quits app)')
        parser.add_argument('--minimized', '-m', action='store_true',
                            help='Starts app minimized to system tray.')
        parser.add_argument('--allow-multiple', '-a', action='store_true',
                            help='Allows multiple instances of the app to run on the same profile')
        parser.add_argument('--no-custom-webengine', action='store_true',
                            help='Uses built-in QWebEngineView instead of the custom one we use.')
        parser.add_argument('--search-top', action='store_true',
                            help='Puts search bar on top of window when activated')

        parser.add_argument('--version', '-v', action='store_true',
                            help='Prints the version of the app and exits')

        parser.add_argument('--debug', '-d', action='store_true',
                            help='Makes app print more debug messages during execution')

        return parser.parse_args()
