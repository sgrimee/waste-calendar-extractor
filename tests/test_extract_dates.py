#!/usr/bin/env python3
"""
Unit tests for waste collection calendar extractor.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

from waste_calendar_extractor import (
    MONTH_NUMBERS,
    WASTE_TYPE_KEYWORDS,
    detect_month,
    extract_date_and_waste_types,
    generate_ical_calendar,
    group_elements_by_rows,
)


class TestGroupElementsByRows(unittest.TestCase):
    """Test the group_elements_by_rows function."""

    def test_empty_elements(self):
        """Test with empty elements list."""
        result = group_elements_by_rows([])
        self.assertEqual(result, [])

    def test_single_element(self):
        """Test with single element."""
        elements = [{"text": "test", "x": 10, "y": 20}]
        result = group_elements_by_rows(elements)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], elements)

    def test_elements_same_row(self):
        """Test elements on same row (similar Y coordinates)."""
        elements = [{"text": "date", "x": 10, "y": 20}, {"text": "type", "x": 50, "y": 22}]
        result = group_elements_by_rows(elements, row_tolerance=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 2)

    def test_elements_different_rows(self):
        """Test elements on different rows."""
        elements = [{"text": "date1", "x": 10, "y": 20}, {"text": "date2", "x": 10, "y": 40}]
        result = group_elements_by_rows(elements, row_tolerance=5)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(len(result[1]), 1)


class TestDetectMonth(unittest.TestCase):
    """Test the detect_month function."""

    def test_detect_january(self):
        """Test detecting January in Luxembourgish."""
        text = "Some text\nJANUAR | JANVIER\nMore text"
        result = detect_month(text)
        self.assertEqual(result, "JANUAR")

    def test_detect_march(self):
        """Test detecting March in Luxembourgish."""
        text = "Calendar page\nMÄERZ | MARS\nDates..."
        result = detect_month(text)
        self.assertEqual(result, "MÄERZ")

    def test_no_month_found(self):
        """Test when no month is found."""
        text = "Just some random text\nwithout any months"
        result = detect_month(text)
        self.assertEqual(result, "")

    def test_first_month_wins(self):
        """Test that first month found is returned."""
        text = "JANUAR and FEBRUAR both here"
        result = detect_month(text)
        self.assertEqual(result, "JANUAR")


class TestExtractDateAndWasteTypes(unittest.TestCase):
    """Test the extract_date_and_waste_types function."""

    def test_extract_date_only(self):
        """Test extracting just a date."""
        row = [{"text": "15"}, {"text": "Some other text"}]
        date_found, waste_types = extract_date_and_waste_types(row)
        self.assertEqual(date_found, 15)
        self.assertEqual(waste_types, [])

    def test_extract_waste_type_only(self):
        """Test extracting just waste type."""
        row = [{"text": "Reschtoffäll | Déchets ménagers"}, {"text": "Other"}]
        date_found, waste_types = extract_date_and_waste_types(row)
        self.assertIsNone(date_found)
        self.assertEqual(len(waste_types), 1)
        self.assertIn("Reschtoffäll | Déchets ménagers", waste_types)

    def test_extract_date_and_waste_type(self):
        """Test extracting both date and waste type."""
        row = [{"text": "8"}, {"text": "Packaging | (VALORLUX)"}]
        date_found, waste_types = extract_date_and_waste_types(row)
        self.assertEqual(date_found, 8)
        self.assertEqual(len(waste_types), 1)
        self.assertIn("Packaging | (VALORLUX)", waste_types)

    def test_invalid_date(self):
        """Test with invalid date (outside 1-31 range)."""
        row = [{"text": "99"}, {"text": "Paper"}]
        date_found, waste_types = extract_date_and_waste_types(row)
        self.assertIsNone(date_found)
        self.assertEqual(len(waste_types), 1)

    def test_multiple_waste_types(self):
        """Test extracting multiple waste types."""
        row = [{"text": "3"}, {"text": "Organesch Ressourcen"}, {"text": "Paper and carton"}]
        date_found, waste_types = extract_date_and_waste_types(row)
        self.assertEqual(date_found, 3)
        self.assertEqual(len(waste_types), 2)


class TestGenerateIcalCalendar(unittest.TestCase):
    """Test the generate_ical_calendar function."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("waste_calendar_extractor.Calendar")
    def test_generate_calendar_with_events(self, mock_calendar_class, mock_file):
        """Test generating calendar with events."""
        # Setup mock calendar
        mock_calendar = Mock()
        mock_calendar_class.return_value = mock_calendar

        # Test data
        results = [
            {"date": datetime(2024, 1, 1), "icons": "Residual waste"},
            {"date": datetime(2024, 1, 8), "icons": "Paper | Carton"},
        ]

        # Call function
        events_added = generate_ical_calendar(results, "test.ics", 2024)

        # Verify
        self.assertEqual(events_added, 2)
        mock_file.assert_called_once_with("test.ics", "w", encoding="utf-8")
        self.assertEqual(mock_calendar.events.add.call_count, 2)

    @patch("builtins.open", new_callable=mock_open)
    @patch("waste_calendar_extractor.Calendar")
    def test_generate_calendar_empty_icons(self, mock_calendar_class, mock_file):
        """Test generating calendar with empty icons (should skip)."""
        # Setup mock calendar
        mock_calendar = Mock()
        mock_calendar_class.return_value = mock_calendar

        # Test data with empty icons
        results = [
            {"date": datetime(2024, 1, 1), "icons": ""},
            {
                "date": datetime(2024, 1, 2),
                "icons": "   ",  # Just whitespace
            },
        ]

        # Call function
        events_added = generate_ical_calendar(results, "test.ics", 2024)

        # Verify no events added
        self.assertEqual(events_added, 0)
        mock_file.assert_called_once_with("test.ics", "w", encoding="utf-8")


class TestConstants(unittest.TestCase):
    """Test module constants."""

    def test_month_numbers_mapping(self):
        """Test that month numbers are correctly mapped."""
        self.assertEqual(MONTH_NUMBERS["JANUAR"], 1)
        self.assertEqual(MONTH_NUMBERS["FEBRUAR"], 2)
        self.assertEqual(MONTH_NUMBERS["MÄERZ"], 3)
        self.assertEqual(MONTH_NUMBERS["DEZEMBER"], 12)
        self.assertEqual(len(MONTH_NUMBERS), 12)

    def test_waste_type_keywords(self):
        """Test that waste type keywords include expected values."""
        self.assertIn("reschtoffäll", WASTE_TYPE_KEYWORDS)
        self.assertIn("paper", WASTE_TYPE_KEYWORDS)
        self.assertIn("glas", WASTE_TYPE_KEYWORDS)
        self.assertIn("packaging", WASTE_TYPE_KEYWORDS)
        self.assertIn("organic", WASTE_TYPE_KEYWORDS)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_full_workflow_mock_data(self):
        """Test the full workflow with mock data."""
        # This would test the main extract_dates_from_pdf function
        # with mocked PDF data, but that's complex to set up properly
        # In a real scenario, you'd create test PDF files
        pass


if __name__ == "__main__":
    unittest.main()
