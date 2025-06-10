#!/usr/bin/env python3
"""
Unit tests for module constants.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from waste_calendar_extractor import MONTH_NUMBERS, WASTE_TYPE_KEYWORDS


def test_month_numbers_mapping():
    """Test that month numbers are correctly mapped."""
    assert MONTH_NUMBERS["JANUAR"] == 1
    assert MONTH_NUMBERS["FEBRUAR"] == 2
    assert MONTH_NUMBERS["MÄERZ"] == 3
    assert MONTH_NUMBERS["DEZEMBER"] == 12
    assert len(MONTH_NUMBERS) == 12


def test_waste_type_keywords():
    """Test that waste type keywords include expected values."""
    assert "reschtoffäll" in WASTE_TYPE_KEYWORDS
    assert "paper" in WASTE_TYPE_KEYWORDS
    assert "glas" in WASTE_TYPE_KEYWORDS
    assert "packaging" in WASTE_TYPE_KEYWORDS
    assert "organic" in WASTE_TYPE_KEYWORDS
