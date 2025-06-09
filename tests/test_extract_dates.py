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
    extract_language_from_waste_description,
    generate_ical_calendar,
    get_waste_type_icon,
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
    @patch("waste_calendar_extractor.output_generator.Calendar")
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
    @patch("waste_calendar_extractor.output_generator.Calendar")
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


class TestExtractLanguageFromWasteDescription(unittest.TestCase):
    """Test the extract_language_from_waste_description function."""

    def test_extract_german(self):
        """Test extracting German/Luxembourgish text."""
        description = "Reschtoffäll | Déchets ménagers | Residual waste"
        result = extract_language_from_waste_description(description, "de")
        self.assertEqual(result, "Reschtoffäll")

    def test_extract_french(self):
        """Test extracting French text."""
        description = "Pabeier a Kartong | Papier et carton | Paper and carton"
        result = extract_language_from_waste_description(description, "fr")
        self.assertEqual(result, "Papier et carton")

    def test_extract_english(self):
        """Test extracting English text."""
        description = "Glas | Verre | Glass"
        result = extract_language_from_waste_description(description, "en")
        self.assertEqual(result, "Glass")

    def test_fallback_to_first_part(self):
        """Test fallback to first part when language not found."""
        description = "Unknown term | Other term"
        result = extract_language_from_waste_description(description, "de")
        self.assertEqual(result, "Unknown term")

    def test_single_part_description(self):
        """Test with single part description."""
        description = "Reschtoffäll"
        result = extract_language_from_waste_description(description, "de")
        self.assertEqual(result, "Reschtoffäll")

    def test_valorlux_packaging_english(self):
        """Test VALORLUX packaging recognition."""
        description = "Verpackungen | (VALORLUX) | Packaging"
        result = extract_language_from_waste_description(description, "en")
        self.assertEqual(result, "Packaging")

    def test_christmas_trees_german(self):
        """Test Christmas trees in German."""
        description = "Beemercher | Sapins de Noël | Christmas trees"
        result = extract_language_from_waste_description(description, "de")
        self.assertEqual(result, "Beemercher")

    def test_old_clothes_french(self):
        """Test old clothes in French."""
        description = "Aalt Gezei | Vieux vêtements | Old clothes"
        result = extract_language_from_waste_description(description, "fr")
        self.assertEqual(result, "Vieux vêtements")


class TestGetWasteTypeIcon(unittest.TestCase):
    """Test the get_waste_type_icon function."""

    def test_residual_waste_icon(self):
        """Test icon for residual waste."""
        self.assertEqual(get_waste_type_icon("Reschtoffäll"), "🗑️")
        self.assertEqual(get_waste_type_icon("Déchets ménagers"), "🗑️")
        self.assertEqual(get_waste_type_icon("Residual waste"), "🗑️")

    def test_paper_icon(self):
        """Test icon for paper."""
        self.assertEqual(get_waste_type_icon("Pabeier a Kartong"), "📄")
        self.assertEqual(get_waste_type_icon("Papier et carton"), "📄")
        self.assertEqual(get_waste_type_icon("Paper and carton"), "📄")

    def test_glass_icon(self):
        """Test icon for glass."""
        self.assertEqual(get_waste_type_icon("Glas"), "🪟")
        self.assertEqual(get_waste_type_icon("Verre"), "🪟")
        self.assertEqual(get_waste_type_icon("Glass"), "🪟")

    def test_packaging_icon(self):
        """Test icon for packaging."""
        self.assertEqual(get_waste_type_icon("(VALORLUX)"), "📦")
        self.assertEqual(get_waste_type_icon("Packaging"), "📦")
        self.assertEqual(get_waste_type_icon("Emballages"), "📦")

    def test_organic_icon(self):
        """Test icon for organic waste."""
        self.assertEqual(get_waste_type_icon("Organesch Ressourcen"), "🌱")
        self.assertEqual(get_waste_type_icon("Ressources organiques"), "🌱")

    def test_clothes_icon(self):
        """Test icon for old clothes."""
        self.assertEqual(get_waste_type_icon("Aalt Gezei"), "👕")
        self.assertEqual(get_waste_type_icon("Vieux vêtements"), "👕")
        self.assertEqual(get_waste_type_icon("Old clothes"), "👕")

    def test_christmas_trees_icon(self):
        """Test icon for Christmas trees."""
        self.assertEqual(get_waste_type_icon("Beemercher"), "🎄")
        self.assertEqual(get_waste_type_icon("Sapins de Noël"), "🎄")
        self.assertEqual(get_waste_type_icon("Christmas trees"), "🎄")

    def test_default_icon(self):
        """Test default icon for unknown waste type."""
        self.assertEqual(get_waste_type_icon("Unknown waste type"), "♻️")


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
