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
##################################################################################
"""
import sys
from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSystemTrayIcon, \
    QMenu

from websiteapp.about import About
from websiteapp.const import Const
from websiteapp.utils import Utils


class WebApp(QMainWindow):
    about_dialog: Optional[About] = None

    def __init__(self):
        super().__init__()

        self.app = QApplication.instance()
        self.args = Utils.handle_args()

        # Set window geometry
        x, y, width, height = Utils.parse_geometry(self.args.geometry)
        self.setGeometry(x, y, width, height)
        self.dbug(f'Geometry: {width}x{height}+{x}+{y}')

        app_icon = Utils.get_icon(self.args.icon)
        self.setWindowIcon(app_icon)
        if self.args.no_tray:
            self.app.setQuitOnLastWindowClosed(True)  # Ensure we quit when last window is closed
        else:
            self.setup_tray_icon(app_icon)

        window_title = self.args.name if self.args.name else self.args.url
        window_title += f' ({self.args.profile})' if self.args.debug else ''
        self.setWindowTitle(f'{window_title} · {Const.APP_NAME}')

        # Create a persistent profile (cookie jar etc.)
        self.dbug(f'Profile: {self.args.profile}')
        self.profile = QWebEngineProfile(self.args.profile, self)
        self.page = QWebEnginePage(self.profile, self)

        self.browser = QWebEngineView(self)
        web_settings = self.browser.settings()
        web_settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)

        self.browser.setPage(self.page)
        self.browser.setZoomFactor(self.args.zoom)

        self.dbug(f'URL: {self.args.url}')
        self.browser.setUrl(QUrl(self.args.url))

        # Window layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.browser)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event) -> None:
        """
        Override closeEvent to hide the window instead of closing it and hides the window instead.

        :param event:
        """
        if not self.args.no_tray:
            self.hide()
            event.ignore()
        else:
            super().closeEvent(event)

    def setup_tray_icon(self, icon) -> None:
        """
        This method is used to set up the system tray icon for the application.

        :param icon: QPixmap object representing the icon that will be used in the system tray.
        """
        tray_menu = QMenu()

        tray_icon = QSystemTrayIcon(icon, self.app)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.activated.connect(self.on_tray_icon_activated)

        about_label = f'About {Const.APP_NAME}'
        about_action = QAction(about_label, self.app)
        about_action.triggered.connect(self.open_about_dialog)
        tray_menu.addAction(about_action)

        quit_label = f'Quit {self.args.name}' if self.args.name else 'Quit'
        quit_action = QAction(quit_label, self.app)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        tray_icon.show()

    def quit_app(self) -> None:
        """
        Closes the application.
        """
        self.app.quit()

    def open_about_dialog(self) -> None:
        """
        Opens the about dialog.
        """
        if not self.about_dialog:
            self.about_dialog = About()

        if not self.about_dialog.isVisible():
            self.about_dialog.show()
        self.about_dialog.activateWindow()

    def on_tray_icon_activated(self, reason) -> None:
        """
        Callback invoked when application icon in system tray is clicked.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Check for left-click (Trigger)
            self.toggle_window()

    def toggle_window(self) -> None:
        """
        Toggles the visibility of the window.
        """
        self.hide() if self.isVisible() else self.show()

    # ############################################################################################ #

    def dbug(self, msg: str) -> None:
        if self.args.debug:
            print(msg, file=sys.stderr)

    # ############################################################################################ #

    @staticmethod
    def run() -> None:
        """
        Application entry point. When renamed, ensure setup.py's reference is updated as well.
        """
        app = QApplication(sys.argv)
        app.setOrganizationName("MarcinOrlowski")
        app.setApplicationName("Website As App")

        window = WebApp()
        window.show()

        app.exec()
