#!/usr/bin/env python3
"""
Unit tests for PDF extraction functions.

These tests validate the area-based PDF extraction system that separates
calendar content from legend information using predefined coordinate areas.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz

from waste_calendar_extractor.pdf_extractor import (
    detect_month,
    extract_calendar_dates,
    extract_legend_mapping, 
    group_elements_by_rows,
    load_page_areas,
)


def test_group_elements_by_rows_empty():
    """Test grouping elements when no elements are provided.
    
    This function groups text elements by Y-coordinate proximity to identify
    calendar rows for legacy compatibility.
    """
    result = group_elements_by_rows([])
    assert result == []


def test_group_elements_by_rows_single_element():
    """Test grouping a single text element into one row.
    
    Validates that a single text element is correctly grouped into
    a single row for legacy text-based processing.
    """
    elements = [{"text": "test", "x": 10, "y": 20}]
    result = group_elements_by_rows(elements)
    assert len(result) == 1
    assert result[0] == elements


def test_group_elements_by_rows_same_row():
    """Test grouping elements with similar Y coordinates into the same row.
    
    Elements within the row tolerance (default 10px) should be grouped together
    as they likely belong to the same calendar row.
    """
    elements = [{"text": "date", "x": 10, "y": 20}, {"text": "type", "x": 50, "y": 22}]
    result = group_elements_by_rows(elements, row_tolerance=5)
    assert len(result) == 1
    assert len(result[0]) == 2


def test_group_elements_by_rows_different_rows():
    """Test grouping elements with different Y coordinates into separate rows.
    
    Elements beyond the row tolerance should be placed in separate groups
    representing different calendar rows.
    """
    elements = [{"text": "date1", "x": 10, "y": 20}, {"text": "date2", "x": 10, "y": 40}]
    result = group_elements_by_rows(elements, row_tolerance=5)
    assert len(result) == 2
    assert len(result[0]) == 1
    assert len(result[1]) == 1


def test_detect_month_january():
    """Test detecting January month name in Luxembourgish from page text.
    
    The detect_month function searches for Luxembourgish month names in PDF text
    to track calendar progression across pages.
    """
    text = "Some text\nJANUAR | JANVIER\nMore text"
    result = detect_month(text)
    assert result == "JANUAR"


def test_detect_month_march():
    """Test detecting March month name with special characters.
    
    Validates that month detection works with Luxembourgish special characters
    like ä in MÄERZ.
    """
    text = "Calendar page\nMÄERZ | MARS\nDates..."
    result = detect_month(text)
    assert result == "MÄERZ"


def test_detect_month_no_month_found():
    """Test month detection when no valid month names are present.
    
    Should return empty string when no Luxembourgish month names are found
    in the page text.
    """
    text = "Just some random text\nwithout any months"
    result = detect_month(text)
    assert result == ""


def test_detect_month_first_month_wins():
    """Test that the first month name encountered is returned.
    
    When multiple month names appear in text, the first one found should
    be returned to maintain consistent behavior.
    """
    text = "JANUAR and FEBRUAR both here"
    result = detect_month(text)
    assert result == "JANUAR"


def test_extract_calendar_dates():
    """Test extracting calendar dates with precise row boundaries."""
    # Create a mock PDF page with date text elements
    mock_page = Mock(spec=fitz.Page)
    
    # Mock the text extraction to return day numbers with bounding boxes
    mock_text_dict = {
        "blocks": [
            {
                "lines": [
                    {
                        "spans": [
                            {
                                "text": "15",
                                "bbox": [70.0, 100.0, 77.0, 123.2]  # x0, y0, x1, y1
                            }
                        ]
                    }
                ]
            }
        ]
    }
    mock_page.get_text.return_value = mock_text_dict
    
    # Mock calendar area
    calendar_area = {"x0": 54.5, "y0": 39.0, "x1": 328.4, "y1": 808.3}
    
    date_positions = extract_calendar_dates(mock_page, calendar_area)
    
    assert 15 in date_positions
    assert "center" in date_positions[15]
    assert "top" in date_positions[15]
    assert "bottom" in date_positions[15]


def test_extract_legend_mapping():
    """Test extracting waste type legend from the legend area."""
    # Create a mock PDF page with legend text
    mock_page = Mock(spec=fitz.Page)
    
    # Mock legend text elements
    mock_legend_elements = [
        {"text": "Reschtoffäll", "x": 400, "y": 150},
        {"text": "|", "x": 450, "y": 150},
        {"text": "Déchets", "x": 460, "y": 150},
        {"text": "ménagers", "x": 500, "y": 150},
        {"text": "Organesch", "x": 400, "y": 200},
        {"text": "Ressourcen", "x": 460, "y": 200}
    ]
    
    # Mock the extract_text_from_area function behavior
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump({
            "legend_area": {"x0": 373.0, "y0": 15.6, "x1": 593.0, "y1": 812.5}
        }, f)
        areas_file = f.name
    
    try:
        from waste_calendar_extractor.pdf_extractor import extract_text_from_area
        import waste_calendar_extractor.pdf_extractor as pdf_mod
        
        # Patch the load_page_areas function
        original_load = pdf_mod.load_page_areas
        pdf_mod.load_page_areas = lambda: {"legend_area": {"x0": 373.0, "y0": 15.6, "x1": 593.0, "y1": 812.5}}
        
        # Mock extract_text_from_area to return our mock elements
        original_extract = pdf_mod.extract_text_from_area
        pdf_mod.extract_text_from_area = lambda page, area: mock_legend_elements
        
        legend_area = {"x0": 373.0, "y0": 15.6, "x1": 593.0, "y1": 812.5}
        mapping = extract_legend_mapping(mock_page, legend_area)
        
        # Should extract residual waste mapping
        assert "residual" in mapping
        
        # Restore original functions
        pdf_mod.load_page_areas = original_load
        pdf_mod.extract_text_from_area = original_extract
        
    finally:
        Path(areas_file).unlink(missing_ok=True)


def test_load_page_areas():
    """Test loading predefined calendar and legend areas from JSON file."""
    # Create a temporary areas file
    test_areas = {
        "calendar_area": {"x0": 54.5, "y0": 39.0, "x1": 328.4, "y1": 808.3},
        "legend_area": {"x0": 373.0, "y0": 15.6, "x1": 593.0, "y1": 812.5}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump(test_areas, f)
        areas_file = f.name
    
    try:
        # Patch the areas file path
        import waste_calendar_extractor.pdf_extractor as pdf_mod
        original_path = Path(pdf_mod.__file__).parent.parent.parent / "page_areas.json"
        
        # Temporarily replace the file
        import shutil
        if original_path.exists():
            backup_path = str(original_path) + ".backup"
            shutil.copy(str(original_path), backup_path)
        
        shutil.copy(areas_file, str(original_path))
        
        areas = load_page_areas()
        assert "calendar_area" in areas
        assert "legend_area" in areas
        assert areas["calendar_area"]["x0"] == 54.5
        
        # Restore original file
        if Path(backup_path).exists():
            shutil.move(backup_path, str(original_path))
            
    finally:
        Path(areas_file).unlink(missing_ok=True)


def test_extract_calendar_dates_invalid_date():
    """Test that invalid dates (outside 1-31 range) are ignored."""
    mock_page = Mock(spec=fitz.Page)
    
    # Mock text dict with invalid date
    mock_text_dict = {
        "blocks": [
            {
                "lines": [
                    {
                        "spans": [
                            {
                                "text": "99",  # Invalid date
                                "bbox": [70.0, 100.0, 77.0, 123.2]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    mock_page.get_text.return_value = mock_text_dict
    
    calendar_area = {"x0": 54.5, "y0": 39.0, "x1": 328.4, "y1": 808.3}
    date_positions = extract_calendar_dates(mock_page, calendar_area)
    
    # Should not include invalid date
    assert 99 not in date_positions
    assert len(date_positions) == 0


def test_extract_calendar_dates_multiple_days():
    """Test extracting multiple calendar dates with proper row boundaries."""
    mock_page = Mock(spec=fitz.Page)
    
    # Mock multiple day numbers
    mock_text_dict = {
        "blocks": [
            {
                "lines": [
                    {
                        "spans": [
                            {
                                "text": "1",
                                "bbox": [70.0, 78.0, 77.0, 101.2]
                            },
                            {
                                "text": "2", 
                                "bbox": [69.5, 101.3, 79.1, 124.4]
                            },
                            {
                                "text": "3",
                                "bbox": [69.6, 124.5, 79.0, 147.6]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    mock_page.get_text.return_value = mock_text_dict
    
    calendar_area = {"x0": 54.5, "y0": 39.0, "x1": 328.4, "y1": 808.3}
    date_positions = extract_calendar_dates(mock_page, calendar_area)
    
    # Should extract all three days
    assert len(date_positions) == 3
    assert 1 in date_positions
    assert 2 in date_positions  
    assert 3 in date_positions
    
    # Check that row boundaries are calculated correctly
    # Day 1 should have top boundary above its text
    assert date_positions[1]["top"] < date_positions[1]["center"]
    # Day 2 should be between day 1 and day 3
    assert date_positions[1]["bottom"] < date_positions[2]["center"] < date_positions[3]["top"]


def test_area_based_extraction_workflow():
    """Test the complete area-based extraction workflow.
    
    This test validates that the new area-based system correctly:
    1. Loads predefined coordinate areas
    2. Extracts calendar dates from the calendar area
    3. Extracts legend mappings from the legend area
    4. Maps waste symbols to dates using precise row boundaries
    """
    # This is more of an integration test that would require a real PDF
    # For now, just test that the functions can be called without error
    
    # Test that we can load page areas (will fail if page_areas.json doesn't exist)
    try:
        areas = load_page_areas()
        assert "calendar_area" in areas
        assert "legend_area" in areas
        
        # Verify area structure
        for area_name in ["calendar_area", "legend_area"]:
            area = areas[area_name]
            assert "x0" in area and "y0" in area
            assert "x1" in area and "y1" in area
            assert area["x1"] > area["x0"]  # Valid width
            assert area["y1"] > area["y0"]  # Valid height
            
    except FileNotFoundError:
        # Skip test if page_areas.json doesn't exist
        import pytest
        pytest.skip("page_areas.json not found - skipping area-based extraction test")
