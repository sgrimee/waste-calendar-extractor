"""Unit tests for calendar_processor module."""

import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from waste_cal.calendar_processor import CalendarData, extract_calendar_data
from waste_cal.waste_types import Languages, WasteType


class TestCalendarData:
    """Test CalendarData class."""

    def test_init(self):
        """Test CalendarData initialization."""
        calendar_data = CalendarData()
        assert calendar_data.get_all_dates() == []

    def test_add_collection_new_date(self):
        """Test adding collection to a new date."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)

        calendar_data.add_collection(date, WasteType.RESIDUAL)

        collections = calendar_data.get_collections_for_date(date)
        assert collections == [WasteType.RESIDUAL]

    def test_add_collection_existing_date(self):
        """Test adding multiple collections to the same date."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)

        calendar_data.add_collection(date, WasteType.RESIDUAL)
        calendar_data.add_collection(date, WasteType.PAPER)

        collections = calendar_data.get_collections_for_date(date)
        assert WasteType.RESIDUAL in collections
        assert WasteType.PAPER in collections
        assert len(collections) == 2

    def test_add_collection_duplicate_prevention(self):
        """Test that duplicate waste types for same date are prevented."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)

        calendar_data.add_collection(date, WasteType.RESIDUAL)
        calendar_data.add_collection(date, WasteType.RESIDUAL)  # Duplicate

        collections = calendar_data.get_collections_for_date(date)
        assert collections == [WasteType.RESIDUAL]
        assert len(collections) == 1

    def test_get_collections_for_date_empty(self):
        """Test getting collections for date with no collections."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)

        collections = calendar_data.get_collections_for_date(date)
        assert collections == []

    def test_get_all_dates_sorted(self):
        """Test that get_all_dates returns dates in chronological order."""
        calendar_data = CalendarData()

        # Add dates in random order
        date3 = datetime.date(2025, 3, 15)
        date1 = datetime.date(2025, 1, 15)
        date2 = datetime.date(2025, 2, 15)

        calendar_data.add_collection(date3, WasteType.RESIDUAL)
        calendar_data.add_collection(date1, WasteType.PAPER)
        calendar_data.add_collection(date2, WasteType.GLASS)

        all_dates = calendar_data.get_all_dates()
        assert all_dates == [date1, date2, date3]

    def test_to_text_empty(self):
        """Test to_text with empty calendar data."""
        calendar_data = CalendarData()

        result = calendar_data.to_text()
        assert result == "No waste collections found."

    def test_to_text_single_date(self):
        """Test to_text with single date and waste type."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)
        calendar_data.add_collection(date, WasteType.RESIDUAL)

        result = calendar_data.to_text(Languages.EN)

        assert "=== January 2025 ===" in result
        assert "2025-01-15 (Wednesday)" in result
        assert "Residual waste 🗑️" in result

    def test_to_text_multiple_waste_types_same_date(self):
        """Test to_text with multiple waste types on same date."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)
        calendar_data.add_collection(date, WasteType.RESIDUAL)
        calendar_data.add_collection(date, WasteType.PAPER)

        result = calendar_data.to_text(Languages.EN)

        assert "Paper and cardboard 📄, Residual waste 🗑️" in result

    def test_to_text_multiple_months(self):
        """Test to_text with dates spanning multiple months."""
        calendar_data = CalendarData()

        jan_date = datetime.date(2025, 1, 15)
        feb_date = datetime.date(2025, 2, 15)

        calendar_data.add_collection(jan_date, WasteType.RESIDUAL)
        calendar_data.add_collection(feb_date, WasteType.PAPER)

        result = calendar_data.to_text(Languages.EN)

        assert "=== January 2025 ===" in result
        assert "=== February 2025 ===" in result
        assert "2025-01-15" in result
        assert "2025-02-15" in result

    def test_to_text_different_languages(self):
        """Test to_text with different languages."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)
        calendar_data.add_collection(date, WasteType.RESIDUAL)

        # Test English
        result_en = calendar_data.to_text(Languages.EN)
        assert "Residual waste" in result_en

        # Test French
        result_fr = calendar_data.to_text(Languages.FR)
        assert "Déchets ménagers" in result_fr

        # Test Luxembourgish
        result_lu = calendar_data.to_text(Languages.LU)
        assert "Reschtoffäll" in result_lu

    def test_to_text_waste_types_sorted(self):
        """Test that waste types are sorted alphabetically by value."""
        calendar_data = CalendarData()
        date = datetime.date(2025, 1, 15)

        # Add waste types in non-alphabetical order
        calendar_data.add_collection(date, WasteType.RESIDUAL)  # "residual"
        calendar_data.add_collection(date, WasteType.ORGANIC)  # "organic"
        calendar_data.add_collection(date, WasteType.GLASS)  # "glass"

        result = calendar_data.to_text(Languages.EN)

        # Should be sorted: glass, organic, residual
        glass_pos = result.find("Glass")
        organic_pos = result.find("Organic")
        residual_pos = result.find("Residual")

        assert glass_pos < organic_pos < residual_pos


class TestExtractCalendarData:
    """Test extract_calendar_data function."""

    @patch("waste_cal.calendar_processor.detect_waste_type_from_drawing")
    @patch("waste_cal.calendar_processor.is_drawing_in_box")
    @patch("waste_cal.calendar_processor.areas_per_day")
    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_basic(self, mock_read_pdf, mock_areas_per_day, mock_is_drawing_in_box, mock_detect):
        """Test basic calendar data extraction."""
        # Setup mocks
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 13  # 12 months + title page
        mock_read_pdf.return_value = mock_doc

        # Mock page
        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page

        # Mock day areas (just one day for January)
        mock_day_area = Mock()
        mock_areas_per_day.return_value = [mock_day_area]

        # Mock drawings
        mock_drawing = Mock()
        mock_page.get_drawings.return_value = [mock_drawing]

        # Mock drawing in box
        mock_is_drawing_in_box.return_value = True

        # Mock waste type detection
        mock_detect.return_value = WasteType.RESIDUAL

        # Execute
        result = extract_calendar_data("test.pdf", 2025)

        # Verify
        assert isinstance(result, CalendarData)

        # Should have found collections for January 1st
        jan_1 = datetime.date(2025, 1, 1)
        collections = result.get_collections_for_date(jan_1)
        assert WasteType.RESIDUAL in collections

        # Verify mocks were called
        mock_read_pdf.assert_called_once_with("test.pdf")
        mock_doc.close.assert_called_once()

    @patch("waste_cal.calendar_processor.read_pdf")
    @patch("waste_cal.calendar_processor.areas_per_day")
    def test_extract_calendar_data_invalid_date(self, mock_areas_per_day, mock_read_pdf):
        """Test extraction handles invalid dates gracefully."""
        # Setup mocks for February
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 13
        mock_read_pdf.return_value = mock_doc

        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page

        # Mock 30 day areas for February (invalid - Feb only has 28/29 days)
        mock_areas_per_day.return_value = [Mock() for _ in range(30)]
        mock_page.get_drawings.return_value = []

        # Execute - should not crash on invalid dates like Feb 30th
        result = extract_calendar_data("test.pdf", 2025)

        assert isinstance(result, CalendarData)
        # Should not have any collections for Feb 30th (invalid date)

    @patch("waste_cal.calendar_processor.detect_waste_type_from_drawing")
    @patch("waste_cal.calendar_processor.is_drawing_in_box")
    @patch("waste_cal.calendar_processor.areas_per_day")
    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_no_waste_type_detected(
        self, mock_read_pdf, mock_areas_per_day, mock_is_drawing_in_box, mock_detect
    ):
        """Test extraction when no waste type is detected from drawing."""
        # Setup mocks
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 13
        mock_read_pdf.return_value = mock_doc

        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page

        mock_day_area = Mock()
        mock_areas_per_day.return_value = [mock_day_area]

        mock_drawing = Mock()
        mock_page.get_drawings.return_value = [mock_drawing]
        mock_is_drawing_in_box.return_value = True

        # Mock no waste type detected
        mock_detect.return_value = None

        # Execute
        result = extract_calendar_data("test.pdf", 2025)

        # Should have no collections since waste type detection returned None
        assert result.get_all_dates() == []

    @patch("waste_cal.calendar_processor.is_drawing_in_box")
    @patch("waste_cal.calendar_processor.areas_per_day")
    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_drawing_not_in_box(self, mock_read_pdf, mock_areas_per_day, mock_is_drawing_in_box):
        """Test extraction when drawing is not in day box."""
        # Setup mocks
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 13
        mock_read_pdf.return_value = mock_doc

        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page

        mock_day_area = Mock()
        mock_areas_per_day.return_value = [mock_day_area]

        mock_drawing = Mock()
        mock_page.get_drawings.return_value = [mock_drawing]

        # Drawing is not in the day box
        mock_is_drawing_in_box.return_value = False

        # Execute
        result = extract_calendar_data("test.pdf", 2025)

        # Should have no collections since drawing was not in day box
        assert result.get_all_dates() == []

    @patch("waste_cal.calendar_processor.areas_per_day")
    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_short_pdf(self, mock_read_pdf, mock_areas_per_day):
        """Test extraction with PDF that has fewer pages than expected."""
        # Setup mock with only 2 pages (should skip months that don't exist)
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2  # Only title page + January

        # Mock the first page (index 1) that should exist
        mock_page = Mock()
        mock_page.get_drawings.return_value = []
        mock_doc.__getitem__.return_value = mock_page
        mock_areas_per_day.return_value = []  # No day areas for short PDF

        mock_read_pdf.return_value = mock_doc

        # Execute - should not crash when trying to access non-existent pages
        result = extract_calendar_data("test.pdf", 2025)

        assert isinstance(result, CalendarData)
        mock_doc.close.assert_called_once()

    @patch("waste_cal.calendar_processor.detect_waste_type_from_drawing")
    @patch("waste_cal.calendar_processor.is_drawing_in_box")
    @patch("waste_cal.calendar_processor.areas_per_day")
    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_multiple_drawings_same_day(
        self, mock_read_pdf, mock_areas_per_day, mock_is_drawing_in_box, mock_detect
    ):
        """Test extraction with multiple drawings in the same day."""
        # Setup mocks
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 13
        mock_read_pdf.return_value = mock_doc

        mock_page = Mock()
        mock_doc.__getitem__.return_value = mock_page

        mock_day_area = Mock()
        mock_areas_per_day.return_value = [mock_day_area]

        # Multiple drawings in the same day
        mock_drawing1 = Mock()
        mock_drawing2 = Mock()
        mock_page.get_drawings.return_value = [mock_drawing1, mock_drawing2]
        mock_is_drawing_in_box.return_value = True

        # Different waste types detected - need to account for all 12 months
        # Each month will have 2 drawings, so we need 24 return values
        mock_detect.side_effect = [WasteType.RESIDUAL, WasteType.PAPER] * 12

        # Execute
        result = extract_calendar_data("test.pdf", 2025)

        # Should have both waste types for January 1st
        jan_1 = datetime.date(2025, 1, 1)
        collections = result.get_collections_for_date(jan_1)
        assert WasteType.RESIDUAL in collections
        assert WasteType.PAPER in collections
        assert len(collections) == 2

    @patch("waste_cal.calendar_processor.read_pdf")
    def test_extract_calendar_data_pdf_cleanup(self, mock_read_pdf):
        """Test that PDF document is properly closed even if exception occurs."""
        mock_doc = MagicMock()
        mock_read_pdf.return_value = mock_doc

        # Make __len__ raise an exception to test cleanup
        mock_doc.__len__.side_effect = Exception("Test exception")

        # Execute - should raise exception but still clean up
        with pytest.raises(Exception, match="Test exception"):
            extract_calendar_data("test.pdf", 2025)

        # Verify cleanup happened
        mock_doc.close.assert_called_once()
