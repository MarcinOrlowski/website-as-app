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

from websiteapp.utils import Utils


class TestParseGeometry:
    def test_returns_x_y_width_height_in_that_order(self):
        """
        The argument reads WIDTHxHEIGHT+X+Y but the return value is
        (x, y, width, height). Guards against the two being transposed during
        a refactor.
        """
        assert Utils.parse_geometry('450x600+10+20') == (10, 20, 450, 600)

    @pytest.mark.parametrize('geometry, expected', [
        ('450x600+0+0', (0, 0, 450, 600)),
        ('1x1+0+0', (0, 0, 1, 1)),
        ('1920x1080+100+200', (100, 200, 1920, 1080)),
        ('3840x2160+2560+0', (2560, 0, 3840, 2160)),
    ])
    def test_accepts_valid_geometry(self, geometry, expected):
        assert Utils.parse_geometry(geometry) == expected

    @pytest.mark.parametrize('geometry', [
        '',
        'bogus',
        '450x600',
        '450x600+0',
        '450x600+0+0+0',
        '450X600+0+0',
        '-450x600+0+0',
        '450x-600+0+0',
        '450x600+-1+0',
        '450x600+0+-1',
        ' 450x600+0+0',
        '450x600+0+0 ',
        '450x600+0+0px',
        'x600+0+0',
        '450x+0+0',
    ])
    def test_rejects_malformed_geometry(self, geometry):
        with pytest.raises(ValueError):
            Utils.parse_geometry(geometry)

    @pytest.mark.parametrize('geometry, field', [
        ('0x600+0+0', 'Width'),
        ('450x0+0+0', 'Height'),
    ])
    def test_rejects_zero_dimensions(self, geometry, field):
        with pytest.raises(ValueError, match=field):
            Utils.parse_geometry(geometry)

    def test_trailing_newline_is_accepted(self):
        """
        Documents a quirk rather than a requirement: Python's '$' also matches
        immediately before a trailing newline, so this string slips past the
        otherwise strict pattern.
        """
        assert Utils.parse_geometry('450x600+0+0\n') == (0, 0, 450, 600)

    def test_negative_offsets_are_unreachable_by_the_guards(self):
        """
        The x < 0 / y < 0 checks inside parse_geometry() are dead code: the pattern
        captures offsets with (\\d+), which cannot match a minus sign, so such input
        is rejected by the format check first. Asserted via the error message.
        """
        with pytest.raises(ValueError, match='Expected WIDTHxHEIGHT'):
            Utils.parse_geometry('450x600+-5+0')
