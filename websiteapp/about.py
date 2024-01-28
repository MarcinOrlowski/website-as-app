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
import webbrowser
import importlib.resources as pkg_resources

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QVBoxLayout, QLabel, QDialog, QPushButton, QHBoxLayout

from websiteapp.const import Const


class About(QDialog):
    def __init__(self):
        super().__init__()

        self.app = QApplication.instance()

        # Set the layout for the dialog
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setWindowTitle(f"About {Const.APP_NAME}")

        # Create a label for the logo image
        logo_label = QLabel(self)
        with pkg_resources.path('websiteapp.icons', 'logo.png') as icon_path:
            icon_file = str(icon_path)
        logo_label.setPixmap(QPixmap(icon_file))
        layout.addWidget(logo_label)

        # Create a label for the credits text
        label_layout = QVBoxLayout()

        label = QLabel(f'<b>{Const.APP_NAME}</b> v{Const.APP_VERSION}', self)
        label.setTextFormat(Qt.RichText)
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(font.pointSize() * 1.7)
        label.setFont(font)
        label_layout.addWidget(label)

        label = QLabel(f'&copy;2023-{Const.APP_YEAR} Marcin Orlowski', self)
        label.setTextFormat(Qt.RichText)
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(font.pointSize() * 1.2)
        label.setFont(font)
        label_layout.addWidget(label)

        label = QLabel(Const.APP_URL, self)
        # label.setTextFormat(Qt.RichText)
        label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(label)

        layout.addLayout(label_layout)

        # # Create a horizontal layout for the buttons
        bt_website = QPushButton("Open project website", self)
        bt_website.clicked.connect(self.on_ok_clicked)
        bt_close = QPushButton("Close", self)
        bt_close.clicked.connect(self.on_cancel_clicked)
        bt_close.setFocus()

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(6, 6, 6, 6)
        button_layout.setSpacing(6)
        button_layout.addWidget(bt_website)
        button_layout.addWidget(bt_close)
        layout.addLayout(button_layout)

    def on_ok_clicked(self):
        webbrowser.open(Const.APP_URL)
        self.reject()

    def on_cancel_clicked(self):
        self.reject()
