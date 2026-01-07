"""
##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2026 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
# @file      websiteapp/bookmarks.py
#
##################################################################################
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class BookmarkManager:
    """Manages bookmarks storage and retrieval."""

    def __init__(self, storage_path: str):
        """
        Initialize the bookmark manager.

        Args:
            storage_path: Directory path where bookmarks.json will be stored
        """
        self.storage_path = storage_path
        self.bookmarks_file = os.path.join(storage_path, 'bookmarks.json')
        self._bookmarks: List[Dict] = []
        self._load()

    def _load(self) -> None:
        """Load bookmarks from the JSON file."""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    self._bookmarks = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._bookmarks = []
        else:
            self._bookmarks = []

    def _save(self) -> None:
        """Save bookmarks to the JSON file."""
        os.makedirs(self.storage_path, exist_ok=True)
        with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(self._bookmarks, f, indent=2, ensure_ascii=False)

    def add(self, url: str, title: Optional[str] = None) -> bool:
        """
        Add a bookmark if it doesn't already exist.

        Args:
            url: The URL to bookmark
            title: Optional title for the bookmark (defaults to URL if not provided)

        Returns:
            True if bookmark was added, False if it already exists
        """
        if self.exists(url):
            return False

        bookmark = {
            'url': url,
            'title': title if title else url,
            'added': datetime.now().isoformat(),
        }
        self._bookmarks.append(bookmark)
        self._save()
        return True

    def get_all(self) -> List[Dict]:
        """
        Get all bookmarks.

        Returns:
            List of bookmark dictionaries
        """
        return self._bookmarks.copy()

    def remove(self, url: str) -> bool:
        """
        Remove a bookmark by URL.

        Args:
            url: The URL to remove

        Returns:
            True if bookmark was found and removed, False otherwise
        """
        initial_len = len(self._bookmarks)
        self._bookmarks = [b for b in self._bookmarks if b['url'] != url]
        if len(self._bookmarks) < initial_len:
            self._save()
            return True
        return False

    def exists(self, url: str) -> bool:
        """
        Check if a URL is already bookmarked.

        Args:
            url: The URL to check

        Returns:
            True if URL is bookmarked, False otherwise
        """
        return any(b['url'] == url for b in self._bookmarks)
