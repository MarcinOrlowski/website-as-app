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
import re
import sys
from typing import Optional

import fasteners
from PySide6.QtCore import QUrl, QFileSystemWatcher, Qt
from PySide6.QtGui import QAction, QPalette
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineScript,
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
from websiteapp.bookmarks import BookmarkManager
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
                sys.exit(0)

        self.setup_activation_listener()

        # Set window geometry
        x, y, width, height = Utils.parse_geometry(self.args.geometry)
        self.setGeometry(x, y, width, height)
        self.dbug(f'Geometry: {width}x{height}+{x}+{y}')

        app_icon = Utils.get_icon(self.args.icon)
        self.setWindowIcon(app_icon)
        if not self.args.no_tray:
            self.setup_tray_icon(app_icon)

        self.app_name = self.args.name if self.args.name else self.args.url
        self.app_name += f' ({self.args.profile})' if self.args.debug else ''
        self.setWindowTitle(f'{self.app_name} · {Const.APP_NAME}')

        # Create a persistent profile (cookie jar etc.)
        self.profile = QWebEngineProfile(self.args.profile, self)
        self.page = QWebEnginePage(self.profile, self)

        self.dbug(f'Profile: {self.args.profile}')
        self.dbug(f'Cache path: {self.profile.cachePath()}')
        self.dbug(f'Persistent storage: {self.profile.persistentStoragePath()}')

        self.bookmark_manager = BookmarkManager(
            self.profile.persistentStoragePath())

        # Defaults to Const.APP_USER_AGENT, see Utils.handle_args()
        self.profile.setHttpUserAgent(self.args.user_agent)

        self.setup_color_scheme()

        # Create and configure the webpage
        self.page = QWebEnginePage(self.profile, self)
        # Connect permission request handler
        self.page.featurePermissionRequested.connect(self.handle_permission_request)

        # Handle downloads
        self.profile.downloadRequested.connect(self.on_download_requested)

        self.browser = CustomWebEngineView(
            self,
            debug=self.args.debug,
            app_name=self.app_name,
            bookmark_manager=self.bookmark_manager,
        )
        self.browser.setPage(self.page)
        self.browser.setZoomFactor(self.args.zoom)

        web_settings = self.browser.settings()

        # Enable all required clipboard permissions
        web_settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard,
            True)
        web_settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        web_settings.setAttribute(
            QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript,
            True)
        # Additional profile settings for clipboard
        self.profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanPaste,
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
        search_position = SearchBarPosition.TOP if self.args.search_top \
            else SearchBarPosition.BOTTOM
        self.search_toolbar = SearchToolBar.setup_for_window(self,
                                                             position=search_position)
        # Add this line to connect the search toolbar to the CustomWebEngineView
        self.browser.set_search_toolbar(self.search_toolbar)

    def setup_color_scheme(self) -> None:
        """
        Makes web content follow a dark desktop theme.

        Chromium paints scrollbars and default form controls light unless the page
        opts into a dark color scheme, so a dark desktop theme alone still leaves
        white scrollbars behind. When the application palette is dark, force the
        root element into the dark color scheme.
        """
        window_color = self.app.palette().color(QPalette.ColorRole.Window)
        if not Utils.is_dark_color(window_color):
            return

        self.dbug('Dark palette detected, forcing dark color scheme')

        source = """
            (function() {
                var apply = function() {
                    if (document.documentElement) {
                        document.documentElement.style.setProperty(
                            'color-scheme', 'dark', 'important');
                    }
                };
                apply();
                document.addEventListener('DOMContentLoaded', apply);
            })();
        """

        script = QWebEngineScript()
        script.setName('websiteapp_dark_color_scheme')
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        script.setSourceCode(source)
        self.profile.scripts().insert(script)

    def acquire_lock(self) -> bool:
        """
        Acquires a lock for the current profile to prevent multiple instances.
        Returns True if lock was acquired, False otherwise.
        """
        sanitized_profile = self.sanitize_profile_name(self.args.profile)
        lock_file = os.path.join(os.path.expanduser("~"),
                                 f".websiteapp_{sanitized_profile}.lock")
        self.lock = fasteners.InterProcessLock(lock_file)
        if not self.lock.acquire(blocking=False):
            self.activate_existing_instance()
            return False
        return True

    def sanitize_profile_name(self, profile_name: str) -> str:
        """
        Sanitizes the profile name to ensure it can be used as a valid file path.

        Args:
            profile_name (str): The profile name to sanitize.

        Returns:
            str: A sanitized version of the profile name suitable for file paths.
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[\\/:*?"<>|]', '_', profile_name)

        # Trim leading/trailing whitespace and ensure it's not empty
        sanitized = sanitized.strip()

        # Fallback to a default name if the sanitized profile is empty
        if not sanitized:
            sanitized = "default_profile"

        return sanitized

    def activate_existing_instance(self) -> None:
        """
        Sends a signal to the existing instance to activate its window.
        """
        self.dbug(
            f"Bringing existing instance: {Const.APP_NAME}, profile: {self.args.profile}")
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
        Checks for activation signals and brings the window to front if received.
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
        Override closeEvent to hide the window instead of closing it and hides
        the window instead.

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

        :param icon: QPixmap icon that will be used in the system tray.
        """
        tray_menu = QMenu()

        tray_icon = QSystemTrayIcon(icon, self.app)
        # Set custom tooltip if name is provided
        tooltip = self.args.name if self.args.name else Const.APP_NAME
        tray_icon.setToolTip(tooltip)
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

    # ############################################################################ #

    def dbug(self, msg: str) -> None:
        if self.args.debug:
            print(msg, file=sys.stderr)

    # ############################################################################ #

    @staticmethod
    def run() -> None:
        """
        Application entry point.
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
