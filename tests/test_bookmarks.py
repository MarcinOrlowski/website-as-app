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

import json
from datetime import datetime

import pytest

from websiteapp.bookmarks import BookmarkManager

URL = 'https://example.com'
OTHER_URL = 'https://other.example.com'


@pytest.fixture
def manager(tmp_path):
    return BookmarkManager(str(tmp_path))


def read_stored(tmp_path):
    with open(str(tmp_path / 'bookmarks.json'), 'r', encoding='utf-8') as handle:
        return json.load(handle)


class TestAdd:
    def test_adds_new_bookmark(self, manager):
        assert manager.add(URL, 'Example') is True
        assert len(manager.get_all()) == 1

    def test_refuses_duplicate_url(self, manager):
        manager.add(URL, 'Example')
        assert manager.add(URL, 'Different title') is False
        assert len(manager.get_all()) == 1

    def test_duplicate_does_not_overwrite_title(self, manager):
        manager.add(URL, 'Original')
        manager.add(URL, 'Replacement')
        assert manager.get_all()[0]['title'] == 'Original'

    def test_title_defaults_to_url(self, manager):
        manager.add(URL)
        assert manager.get_all()[0]['title'] == URL

    def test_stores_url_title_and_timestamp(self, manager):
        manager.add(URL, 'Example')
        bookmark = manager.get_all()[0]
        assert sorted(bookmark.keys()) == ['added', 'title', 'url']
        # Raises if the stored value is not ISO-8601.
        datetime.fromisoformat(bookmark['added'])


class TestRemove:
    def test_removes_known_url(self, manager):
        manager.add(URL)
        assert manager.remove(URL) is True
        assert manager.get_all() == []

    def test_returns_false_for_unknown_url(self, manager):
        manager.add(URL)
        assert manager.remove(OTHER_URL) is False
        assert len(manager.get_all()) == 1

    def test_removes_only_the_matching_entry(self, manager):
        manager.add(URL)
        manager.add(OTHER_URL)
        manager.remove(URL)
        assert [b['url'] for b in manager.get_all()] == [OTHER_URL]


class TestExists:
    def test_reports_known_and_unknown_urls(self, manager):
        manager.add(URL)
        assert manager.exists(URL) is True
        assert manager.exists(OTHER_URL) is False


class TestPersistence:
    def test_survives_a_new_manager_on_the_same_path(self, tmp_path):
        BookmarkManager(str(tmp_path)).add(URL, 'Example')
        reloaded = BookmarkManager(str(tmp_path))
        assert [b['url'] for b in reloaded.get_all()] == [URL]

    def test_removal_is_persisted(self, tmp_path):
        first = BookmarkManager(str(tmp_path))
        first.add(URL)
        first.remove(URL)
        assert BookmarkManager(str(tmp_path)).get_all() == []

    def test_creates_missing_storage_directory(self, tmp_path):
        nested = tmp_path / 'profile' / 'nested'
        manager = BookmarkManager(str(nested))
        manager.add(URL)
        assert (nested / 'bookmarks.json').exists()

    def test_empty_storage_starts_empty(self, manager):
        assert manager.get_all() == []

    def test_unreadable_json_degrades_to_empty(self, tmp_path):
        (tmp_path / 'bookmarks.json').write_text('{not valid json', encoding='utf-8')
        assert BookmarkManager(str(tmp_path)).get_all() == []

    def test_non_ascii_is_written_unescaped(self, tmp_path):
        BookmarkManager(str(tmp_path)).add(URL, 'zażółć gęślą jaźń')
        raw = (tmp_path / 'bookmarks.json').read_text(encoding='utf-8')
        assert 'zażółć gęślą jaźń' in raw
        assert read_stored(tmp_path)[0]['title'] == 'zażółć gęślą jaźń'


class TestGetAllCopySemantics:
    def test_returned_list_is_a_copy(self, manager):
        manager.add(URL)
        borrowed = manager.get_all()
        borrowed.append({'url': 'injected'})
        assert len(manager.get_all()) == 1

    def test_returned_dicts_are_shared(self, manager):
        """
        get_all() uses list.copy(), which is shallow: the dicts inside are the very
        same objects held internally, so callers can mutate stored bookmarks in
        place. Documents current behaviour; a deep copy would change it.
        """
        manager.add(URL, 'Original')
        manager.get_all()[0]['title'] = 'Mutated'
        assert manager.get_all()[0]['title'] == 'Mutated'
