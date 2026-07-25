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

import pytest

from websiteapp.webapp import WebApp


def sanitize(profile_name):
    """
    sanitize_profile_name() never dereferences `self`, so it can be called unbound
    with a None receiver. Promoting it to a @staticmethod would make this helper
    unnecessary.
    """
    return WebApp.sanitize_profile_name(None, profile_name)


class TestSanitizeProfileName:
    """
    The sanitized name decides both lock file names in $HOME, so a change here
    """

    @pytest.mark.parametrize('profile_name', [
        'default',
        'work',
        'my-profile_2',
        'zazolc-gesla-jazn',
    ])
    def test_leaves_safe_names_untouched(self, profile_name):
        assert sanitize(profile_name) == profile_name

    @pytest.mark.parametrize('profile_name, expected', [
        ('a/b', 'a_b'),
        ('a\\b', 'a_b'),
        ('a:b', 'a_b'),
        ('a*b', 'a_b'),
        ('a?b', 'a_b'),
        ('a"b', 'a_b'),
        ('a<b', 'a_b'),
        ('a>b', 'a_b'),
        ('a|b', 'a_b'),
    ])
    def test_replaces_path_hostile_characters(self, profile_name, expected):
        assert sanitize(profile_name) == expected

    def test_replaces_every_offending_character(self):
        assert sanitize('\\/:*?"<>|') == '_' * 9

    @pytest.mark.parametrize('profile_name, expected', [
        ('  padded  ', 'padded'),
        ('\ttabbed\t', 'tabbed'),
    ])
    def test_trims_surrounding_whitespace(self, profile_name, expected):
        assert sanitize(profile_name) == expected

    @pytest.mark.parametrize('profile_name', ['', '   ', '\t\n'])
    def test_falls_back_to_default_when_nothing_survives(self, profile_name):
        assert sanitize(profile_name) == 'default_profile'

    def test_inner_whitespace_is_preserved(self):
        assert sanitize('two words') == 'two words'

    def test_non_ascii_is_preserved(self):
        assert sanitize('zażółć') == 'zażółć'
