"""
##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2024 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
# @file      websiteapp/webengine.py
#
##################################################################################
"""

# Target file: websiteapp/custom_web_view.py

import re
from PySide6.QtWidgets import QMenu, QApplication, QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None, debug=False):
        super().__init__(parent)
        self.debug = debug  # Store the debug flag to conditionally add the dump action
        self.loading = False  # Keep track of whether a page is loading

        # Connect load progress to determine loading status
        self.loadStarted.connect(self.on_load_started)
        self.loadFinished.connect(self.on_load_finished)

    def on_load_started(self):
        """
        Slot called when page load starts.
        """
        self.loading = True

    def on_load_finished(self):
        """
        Slot called when page load finishes.
        """
        self.loading = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        # Add default actions to the context menu using WebAction namespace
        actions = [
            QWebEnginePage.WebAction.Back,
            QWebEnginePage.WebAction.Forward,
            QWebEnginePage.WebAction.Reload,
            QWebEnginePage.WebAction.Stop,
            QWebEnginePage.WebAction.Copy,
            QWebEnginePage.WebAction.Cut,
            QWebEnginePage.WebAction.Paste,
            QWebEnginePage.WebAction.SelectAll
        ]

        for action in actions:
            q_action = self.pageAction(action)
            if action == QWebEnginePage.WebAction.Back:
                # Specifically handle "Back" item to ensure it's enabled/disabled correctly
                q_action.setText("Back")
                # Check if the back action should be disabled
                history = self.history()
                if len(history.backItems(history.count())) <= 1:
                    q_action.setEnabled(False)

            if action == QWebEnginePage.WebAction.Stop:
                # Disable "Stop" action if there is nothing to stop
                if not self.loading:
                    q_action.setEnabled(False)

            # if q_action.isEnabled():  # Only add enabled actions
            menu.addAction(q_action)

        # Add custom action to copy URL
        copy_url_action = QAction("Copy Current URL", self)
        copy_url_action.triggered.connect(self.copy_url_to_clipboard)
        menu.addAction(copy_url_action)

        # Add custom action to open URL from clipboard
        paste_url_action = QAction("Open URL from Clipboard", self)
        paste_url_action.triggered.connect(self.paste_url_from_clipboard)

        # Check if clipboard contains a valid URL
        if self.is_valid_url_in_clipboard():
            paste_url_action.setEnabled(True)
        else:
            paste_url_action.setEnabled(False)

        menu.addAction(paste_url_action)

        # # If debug mode is enabled, add the "Dump Back Stack" option
        # if self.debug:
        #     dump_stack_action = QAction("Dump Back Stack", self)
        #     dump_stack_action.triggered.connect(self.dump_back_stack)
        #     menu.addAction(dump_stack_action)

        # Add custom action to quit the application
        quit_action = QAction("Quit app…", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        # Display the unified context menu at the cursor position
        menu.exec(event.globalPos())

    def copy_url_to_clipboard(self):
        """
        Copies the current page URL to the clipboard.
        """
        current_url = self.url().toString()
        clipboard = QApplication.clipboard()
        clipboard.setText(current_url)

    def paste_url_from_clipboard(self):
        """
        Pastes a URL from the clipboard into the web client if valid. Otherwise, shows an error dialog.
        """
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()

        if self.is_valid_url(clipboard_text):
            self.setUrl(clipboard_text)
        else:
            QMessageBox.warning(self, "Invalid URL", "No valid URL in clipboard found.")

    def dump_back_stack(self):
        """
        Dumps the list of all pages that can be navigated back to.
        """
        history = self.history()
        back_items = history.backItems(history.count())
        print("Back Stack:")
        for item in back_items:
            print(f"  - {item.url().toString()}")

    def quit_app(self):
        """
        Quits the application gracefully.
        """
        QApplication.quit()

    def is_valid_url_in_clipboard(self):
        """
        Checks if the clipboard contains a valid URL.
        """
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text()
        return self.is_valid_url(clipboard_text)

    @staticmethod
    def is_valid_url(url):
        """
        Validates if the given string is a valid URL.
        """
        url_pattern = re.compile(
            r'^(https?|ftp)://'  # http:// or https:// or ftp://
            r'(\w+(\-\w+)*\.)+[a-zA-Z]{2,}'  # domain name
            r'(:\d+)?'  # optional port
            r'(\/[^\s]*)?$'  # optional path
        )
        return bool(url_pattern.match(url))
