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
# @file      websiteapp/toolbar.py
#
##################################################################################
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QToolBar,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QLabel
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWebEngineCore import QWebEnginePage

class SearchBarPosition:
    """Constants for search bar position"""
    TOP = "top"
    BOTTOM = "bottom"

class SearchToolBar(QToolBar):
    def __init__(self, web_view, position=SearchBarPosition.TOP, parent=None):
        """
        Initialize the search toolbar.

        Args:
            web_view: The QWebEngineView instance to search in
            position: Where to place the search bar (TOP or BOTTOM)
            parent: Parent widget
        """
        super().__init__(parent)
        self.web_view = web_view
        self.position = position
        self.setup_ui()
        self.hide()  # Hidden by default

    def setup_ui(self):
        """Set up the user interface elements of the search toolbar."""
        # Create widget to hold the search controls
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 0, 5, 0)

        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.hide)
        layout.addWidget(self.close_button)

        # Search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in page...")
        self.search_input.textChanged.connect(self.on_text_changed)
        self.search_input.returnPressed.connect(lambda: self.find_text(True))
        layout.addWidget(self.search_input)

        # Previous/Next buttons
        self.prev_button = QPushButton("◀")
        self.prev_button.clicked.connect(lambda: self.find_text(False))
        layout.addWidget(self.prev_button)

        self.next_button = QPushButton("▶")
        self.next_button.clicked.connect(lambda: self.find_text(True))
        layout.addWidget(self.next_button)

        # Match counter label
        self.match_label = QLabel()
        layout.addWidget(self.match_label)

        # Add the container to the toolbar
        self.addWidget(container)

        # Setup search options
        self.search_flags = QWebEnginePage.FindFlag(0)  # Default search flags

        # Timer for delayed search (improves performance)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(lambda: self.find_text(True))

    def show_search(self):
        """Show the search toolbar and focus the input field."""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def on_text_changed(self, text):
        """
        Handle search text changes with debouncing.

        Args:
            text: The current text in the search input
        """
        # Reset the timer on each text change
        self.search_timer.stop()
        if text:
            # Start a new timer
            self.search_timer.start(300)  # 300ms delay
        else:
            # Clear the search
            self.web_view.findText("")
            self.match_label.clear()

    def find_text(self, forward=True):
        """
        Perform the text search in the web view.

        Args:
            forward: Search direction (True for forward, False for backward)
        """
        text = self.search_input.text()
        if not text:
            return

        flags = self.search_flags
        if not forward:
            flags |= QWebEnginePage.FindFlag.FindBackward

        def callback(found):
            if not found:
                # No matches found - show in red
                self.search_input.setStyleSheet("QLineEdit { background-color: #fdd; }")
                self.match_label.setText("No matches")
            else:
                # Matches found - restore normal style
                self.search_input.setStyleSheet("")

        self.web_view.findText(text, flags, callback)

    def set_position(self, position):
        """
        Changes the position of the search toolbar.

        Args:
            position: Either SearchBarPosition.TOP or SearchBarPosition.BOTTOM
        """
        self.position = position
        # If the toolbar is currently shown, update its position
        if self.isVisible():
            self.parent().removeToolBar(self)
            area = Qt.ToolBarArea.TopToolBarArea if position == SearchBarPosition.TOP else Qt.ToolBarArea.BottomToolBarArea
            self.parent().addToolBar(area, self)

    def toggle_case_sensitivity(self):
        """Toggle case-sensitive search."""
        if self.search_flags & QWebEnginePage.FindFlag.FindCaseSensitively:
            self.search_flags &= ~QWebEnginePage.FindFlag.FindCaseSensitively
        else:
            self.search_flags |= QWebEnginePage.FindFlag.FindCaseSensitively
        # Re-run the search with new flags
        self.find_text(True)

    @classmethod
    def setup_for_window(cls, webapp_window, position=SearchBarPosition.TOP):
        """
        Creates and sets up a SearchToolBar instance for the given webapp window.
        """
        search_toolbar = cls(webapp_window.browser, position)

        # Add toolbar to the specified position
        area = Qt.ToolBarArea.TopToolBarArea if position == SearchBarPosition.TOP else Qt.ToolBarArea.BottomToolBarArea
        webapp_window.addToolBar(area, search_toolbar)

        # First, remove any existing actions with the same shortcuts
        for action in webapp_window.actions():
            if action.shortcut() in [QKeySequence.StandardKey.Find, Qt.Key.Key_Escape]:
                webapp_window.removeAction(action)

        # Add Ctrl+F shortcut
        search_action = QAction("Find", webapp_window)
        search_action.setShortcut(QKeySequence.StandardKey.Find)
        search_action.triggered.connect(search_toolbar.show_search)
        webapp_window.addAction(search_action)

        # Add Escape shortcut only if search bar is visible
        escape_action = QAction("Close Find", webapp_window)
        escape_action.setShortcut(Qt.Key.Key_Escape)
        escape_action.triggered.connect(lambda: search_toolbar.hide() if search_toolbar.isVisible() else None)
        webapp_window.addAction(escape_action)

        return search_toolbar
