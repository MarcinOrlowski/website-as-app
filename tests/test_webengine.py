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

from websiteapp.webengine import CustomWebEngineView


class TestIsValidUrl:
    """
    is_valid_url() is a @staticmethod over a plain regex, so it needs neither a
    widget instance nor a running QApplication.
    """

    @pytest.mark.parametrize('url', [
        'http://example.com',
        'https://example.com',
        'ftp://example.com',
        'https://sub.example.com',
        'https://my-site.example.com',
        'https://example.com:8443',
        'https://example.com/path/to/page',
        'https://example.com/search?q=1&x=2',
        'https://example.co.uk',
    ])
    def test_accepts_urls(self, url):
        assert CustomWebEngineView.is_valid_url(url) is True

    @pytest.mark.parametrize('url', [
        '',
        'not a url',
        'example.com',
        '//example.com',
        'https://',
        'javascript:alert(1)',
        'data:text/html,<h1>x</h1>',
        'https://example.com with space',
    ])
    def test_rejects_non_urls(self, url):
        assert CustomWebEngineView.is_valid_url(url) is False

    @pytest.mark.parametrize('url', [
        'http://localhost:8080',
        'http://127.0.0.1:8000',
        'file:///tmp/page.html',
        'https://xn--80ak6aa92e.com',
    ])
    def test_known_limitations_are_rejected(self, url):
        """
        Documents current behaviour, not desired behaviour. The pattern demands a hostname
        ending in a letters-only TLD, so loopback names, bare IPs, file:// and punycode all
        fail. Consequence: the "Open URL from Clipboard" menu entry stays greyed out for them.
        """
        assert CustomWebEngineView.is_valid_url(url) is False
