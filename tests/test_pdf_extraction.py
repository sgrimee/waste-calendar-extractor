#!/usr/bin/env python3
"""
Unit tests for PDF extraction functions.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from waste_calendar_extractor import (
    detect_month,
    extract_date_and_waste_types,
    group_elements_by_rows,
)


def test_group_elements_by_rows_empty():
    """Test with empty elements list."""
    result = group_elements_by_rows([])
    assert result == []


def test_group_elements_by_rows_single_element():
    """Test with single element."""
    elements = [{"text": "test", "x": 10, "y": 20}]
    result = group_elements_by_rows(elements)
    assert len(result) == 1
    assert result[0] == elements


def test_group_elements_by_rows_same_row():
    """Test elements on same row (similar Y coordinates)."""
    elements = [{"text": "date", "x": 10, "y": 20}, {"text": "type", "x": 50, "y": 22}]
    result = group_elements_by_rows(elements, row_tolerance=5)
    assert len(result) == 1
    assert len(result[0]) == 2


def test_group_elements_by_rows_different_rows():
    """Test elements on different rows."""
    elements = [{"text": "date1", "x": 10, "y": 20}, {"text": "date2", "x": 10, "y": 40}]
    result = group_elements_by_rows(elements, row_tolerance=5)
    assert len(result) == 2
    assert len(result[0]) == 1
    assert len(result[1]) == 1


def test_detect_month_january():
    """Test detecting January in Luxembourgish."""
    text = "Some text\nJANUAR | JANVIER\nMore text"
    result = detect_month(text)
    assert result == "JANUAR"


def test_detect_month_march():
    """Test detecting March in Luxembourgish."""
    text = "Calendar page\nMÄERZ | MARS\nDates..."
    result = detect_month(text)
    assert result == "MÄERZ"


def test_detect_month_no_month_found():
    """Test when no month is found."""
    text = "Just some random text\nwithout any months"
    result = detect_month(text)
    assert result == ""


def test_detect_month_first_month_wins():
    """Test that first month found is returned."""
    text = "JANUAR and FEBRUAR both here"
    result = detect_month(text)
    assert result == "JANUAR"


def test_extract_date_and_waste_types_date_only():
    """Test extracting just a date."""
    row = [{"text": "15", "x": 150}, {"text": "Some other text", "x": 300}]
    date_found, waste_types = extract_date_and_waste_types(row)
    assert date_found == 15
    assert waste_types == []


def test_extract_date_and_waste_types_waste_type_only():
    """Test extracting just waste type."""
    row = [{"text": "Reschtoffäll | Déchets ménagers", "x": 300}, {"text": "Other", "x": 400}]
    date_found, waste_types = extract_date_and_waste_types(row)
    assert date_found is None
    assert len(waste_types) == 0


def test_extract_date_and_waste_types_both():
    """Test extracting date with visual format (no text-based waste types)."""
    row = [{"text": "8", "x": 150}, {"text": "Packaging | (VALORLUX)", "x": 160}]
    date_found, waste_types = extract_date_and_waste_types(row)
    assert date_found == 8
    assert len(waste_types) == 0  # No waste types since this PDF uses visual indicators


def test_extract_date_and_waste_types_invalid_date():
    """Test with invalid date (outside 1-31 range)."""
    row = [{"text": "99", "x": 150}, {"text": "Paper", "x": 300}]
    date_found, waste_types = extract_date_and_waste_types(row)
    assert date_found is None
    assert len(waste_types) == 0


def test_extract_date_and_waste_types_multiple_waste_types():
    """Test extracting date with multiple text elements (visual format)."""
    row = [{"text": "3", "x": 150}, {"text": "Organesch Ressourcen", "x": 160}, {"text": "Paper and carton", "x": 170}]
    date_found, waste_types = extract_date_and_waste_types(row)
    assert date_found == 3
    assert len(waste_types) == 0  # No waste types since this PDF uses visual indicators


def test_extract_date_and_waste_types_june_hardcoded():
    """Test hardcoded June schedule (temporary implementation)."""
    row = [{"text": "2", "x": 150}]
    date_found, waste_types = extract_date_and_waste_types(row, "JUNI")
    assert date_found == 2
    assert len(waste_types) == 2
    assert "Organesch Ressourcen" in waste_types
    assert "Gréngschtëtsammlung" in waste_types
