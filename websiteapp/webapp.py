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
# @file      websiteapp/webapp.py
#
##################################################################################
"""
import os
import sys
from typing import Optional

import fasteners
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QFileSystemWatcher, Qt
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineSettings,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QMenu,
    QFileDialog,
)

from websiteapp.about import About
from websiteapp.const import Const
from websiteapp.toolbar import SearchToolBar, SearchBarPosition
from websiteapp.utils import Utils
from websiteapp.webengine import CustomWebEngineView


class WebApp(QMainWindow):
    about_dialog: Optional[About] = None
    lock: Optional[fasteners.InterProcessLock] = None
    file_watcher: Optional[QFileSystemWatcher] = None

    def __init__(self):
        super().__init__()

        # Check for --version before full argument parsing
        if '--version' in sys.argv:
            print(f'{Const.APP_NAME} {Const.APP_VERSION}')
            sys.exit(0)

        self.app = QApplication.instance()
        self.args = Utils.handle_args()

        if not self.args.allow_multiple:
            if not self.acquire_lock():
                sys.exit(0)  # Exit silently as we've activated the existing instance

        self.setup_activation_listener()

        # Set window geometry
        x, y, width, height = Utils.parse_geometry(self.args.geometry)
        self.setGeometry(x, y, width, height)
        self.dbug(f'Geometry: {width}x{height}+{x}+{y}')

        app_icon = Utils.get_icon(self.args.icon)
        self.setWindowIcon(app_icon)
        if not self.args.no_tray:
            self.setup_tray_icon(app_icon)

        window_title = self.args.name if self.args.name else self.args.url
        window_title += f' ({self.args.profile})' if self.args.debug else ''
        self.setWindowTitle(f'{window_title} · {Const.APP_NAME}')

        # Create a persistent profile (cookie jar etc.)
        self.dbug(f'Profile: {self.args.profile}')
        self.profile = QWebEngineProfile(self.args.profile, self)
        self.page = QWebEnginePage(self.profile, self)

        # Set Chrome-like user agent
        chrome_version = "115.0.5790.170"  # Using a recent stable Chrome version
        webkit_version = "537.36"  # WebKit version used by Chrome
        user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}"
        self.agent = self.profile.setHttpUserAgent(user_agent)

        # Create and configure the webpage
        self.page = QWebEnginePage(self.profile, self)
        # Connect permission request handler
        self.page.featurePermissionRequested.connect(self.handle_permission_request)

        # Handle downloads
        self.profile.downloadRequested.connect(self.on_download_requested)

        # Modified to use CustomWebEngineView
        if self.args.no_custom_webengine:
            self.browser = QWebEngineView(self)
        else:
            self.browser = CustomWebEngineView(self, debug=self.args.debug)
        self.browser.setPage(self.page)
        self.browser.setZoomFactor(self.args.zoom)

        web_settings = self.browser.settings()

        # Enable all required clipboard permissions
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard,
                                  True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        web_settings.setAttribute(
            QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        # Additional profile settings for clipboard
        self.profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste,
                                             True)

        self.browser.setPage(self.page)
        self.browser.setZoomFactor(self.args.zoom)

        # Ensure the browser widget can receive focus and key events
        self.browser.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.browser.setFocus()

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

        # Setup search toolbar
        search_position = SearchBarPosition.TOP if self.args.search_top else SearchBarPosition.BOTTOM
        self.search_toolbar = SearchToolBar.setup_for_window(self, position=search_position)
        # Add this line to connect the search toolbar to the CustomWebEngineView
        if not self.args.no_custom_webengine:
            self.browser.set_search_toolbar(self.search_toolbar)

    def acquire_lock(self) -> bool:
        """
        Acquires a lock for the current profile to prevent multiple instances.
        Returns True if lock was acquired, False otherwise.
        """
        lock_file = os.path.join(os.path.expanduser("~"), f".websiteapp_{self.args.profile}.lock")
        self.lock = fasteners.InterProcessLock(lock_file)
        if not self.lock.acquire(blocking=False):
            self.activate_existing_instance()
            return False
        return True

    def activate_existing_instance(self) -> None:
        """
        Sends a signal to the existing instance to activate its window.
        """
        self.dbug(f"Bringing existing instance: {Const.APP_NAME}, profile: {self.args.profile}")
        signal_file = os.path.join(os.path.expanduser("~"),
                                   f".websiteapp_{self.args.profile}_signal")
        with open(signal_file, 'w') as f:
            f.write("activate")

    def setup_activation_listener(self) -> None:
        """
        Sets up a file system watcher to listen for activation signals.
        """
        self.file_watcher = QFileSystemWatcher(self)
        signal_file = os.path.join(os.path.expanduser("~"),
                                   f".websiteapp_{self.args.profile}_signal")
        self.file_watcher.addPath(os.path.dirname(signal_file))
        self.file_watcher.directoryChanged.connect(self.check_activation_signal)

    def check_activation_signal(self, path):
        """
        Checks for activation signals and brings the window to front if signal is received.
        """
        signal_file = os.path.join(path, f".websiteapp_{self.args.profile}_signal")
        if os.path.exists(signal_file):
            os.remove(signal_file)
            self.activate_window()

    def activate_window(self) -> None:
        """
        Brings the window to front and restores it if minimized.
        """
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event) -> None:
        """
        Override closeEvent to hide the window instead of closing it and hides the window instead.

        :param event:
        """
        if not self.args.no_tray:
            self.hide()
            event.ignore()
        else:
            if self.lock:
                self.lock.release()
                self.lock = None
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

        show_label = f'Show {self.args.name}' if self.args.name else 'Show'
        show_action = QAction(show_label, self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_label = f'Quit {self.args.name}' if self.args.name else 'Quit'
        quit_action = QAction(quit_label, self.app)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        tray_icon.show()

    def quit_app(self) -> None:
        """
        Closes the application.
        """
        if self.lock:
            self.lock.release()
            self.lock = None
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

        if window.args.minimized and window.args.no_tray:
            # Cannot use --no-tray and --minimized at the same time. Ignoring --minimized
            window.args.minimized = False

        if not window.args.minimized:
            window.show()

        exit_code = app.exec()

        if window.lock:
            window.lock.release()
            window.lock = None

        sys.exit(exit_code)

    def on_download_requested(self, download) -> None:
        """
        Handles file download requests from the web page.
        """
        print('on_download_requested')
        # Prompt the user to select a download location
        suggested_filename = download.downloadFileName()
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested_filename,
                                              options=options)
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setDownloadDirectory(os.path.dirname(path))
            download.accept()
        else:
            download.cancel()

    def handle_permission_request(self, origin, feature) -> None:
        """
        Handle permission requests from the webpage.
        """
        from PySide6.QtWebEngineCore import QWebEnginePage

        self.dbug(f"Permission requested: {feature} from {origin}")

        # Define all clipboard-related features
        clipboard_features = [
            QWebEnginePage.Feature.ClipboardReadWrite,
            QWebEnginePage.Feature.Clipboard,  # For backwards compatibility
        ]

        if feature in clipboard_features:
            self.dbug(f"Granting clipboard permission for feature: {feature}")
            self.page.setFeaturePermission(
                origin,
                feature,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )
        else:
            self.dbug(f"Denying permission for feature: {feature}")
            self.page.setFeaturePermission(
                origin,
                feature,
                QWebEnginePage.PermissionPolicy.PermissionDeniedByUser
            )
