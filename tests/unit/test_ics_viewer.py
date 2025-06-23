"""Unit tests for ics_viewer module."""

import datetime
from unittest.mock import Mock, mock_open, patch

from waste_cal.ics_viewer.viewer import (
    Colors,
    colorize_text,
    format_event_name,
    generate_calendar_view,
    generate_event_listing,
    generate_monthly_calendar,
    generate_summary_statistics,
    get_waste_type_color,
    group_events_by_month,
    load_ics_file,
    view_ics_file,
)


class TestColorizeText:
    """Test colorize_text function."""

    def test_colorize_text_basic(self):
        """Test basic text colorization."""
        result = colorize_text("test", Colors.RED)
        expected = f"{Colors.RED}test{Colors.RESET}"
        assert result == expected

    def test_colorize_text_with_bold(self):
        """Test text colorization with bold formatting."""
        result = colorize_text("test", Colors.RED, bold=True)
        expected = f"{Colors.BOLD}{Colors.RED}test{Colors.RESET}"
        assert result == expected

    def test_colorize_text_without_bold(self):
        """Test text colorization without bold formatting."""
        result = colorize_text("test", Colors.BLUE, bold=False)
        expected = f"{Colors.BLUE}test{Colors.RESET}"
        assert result == expected


class TestGetWasteTypeColor:
    """Test get_waste_type_color function."""

    def test_get_waste_type_color_residual(self):
        """Test color for residual waste emoji."""
        result = get_waste_type_color("Residual waste 🗑️")
        assert result == Colors.RED

    def test_get_waste_type_color_paper(self):
        """Test color for paper emoji."""
        result = get_waste_type_color("Paper 📄")
        assert result == Colors.BLUE

    def test_get_waste_type_color_glass(self):
        """Test color for glass emoji."""
        result = get_waste_type_color("Glass 🪟")
        assert result == Colors.GREEN

    def test_get_waste_type_color_no_emoji(self):
        """Test color for event without recognized emoji."""
        result = get_waste_type_color("Some event without emoji")
        assert result == Colors.WHITE

    def test_get_waste_type_color_multiple_emojis(self):
        """Test color selection with multiple emojis (should return first match)."""
        result = get_waste_type_color("Mixed event 🗑️📄")
        assert result == Colors.RED  # Should match first emoji in WASTE_TYPE_COLORS


class TestFormatEventName:
    """Test format_event_name function."""

    def test_format_event_name_with_emoji(self):
        """Test formatting event name with emoji."""
        result = format_event_name("Residual waste 🗑️")
        expected = colorize_text("Residual waste 🗑️", Colors.RED, bold=True)
        assert result == expected

    def test_format_event_name_without_emoji(self):
        """Test formatting event name without emoji."""
        result = format_event_name("Regular event")
        expected = colorize_text("Regular event", Colors.WHITE, bold=True)
        assert result == expected


class TestLoadIcsFile:
    """Test load_ics_file function."""

    @patch("builtins.open", mock_open(read_data="BEGIN:VCALENDAR\nEND:VCALENDAR"))
    @patch("waste_cal.ics_viewer.viewer.Calendar")
    def test_load_ics_file_success(self, mock_calendar):
        """Test successful loading of iCS file."""
        mock_cal = Mock()
        mock_calendar.return_value = mock_cal

        result = load_ics_file("test.ics")

        assert result == mock_cal
        mock_calendar.assert_called_once_with("BEGIN:VCALENDAR\nEND:VCALENDAR")

    @patch("sys.exit")
    @patch("builtins.print")
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_ics_file_not_found(self, mock_open, mock_print, mock_exit):
        """Test loading non-existent iCS file."""
        load_ics_file("nonexistent.ics")

        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_once()

    @patch("sys.exit")
    @patch("builtins.print")
    @patch("builtins.open", side_effect=Exception("Test error"))
    def test_load_ics_file_exception(self, mock_open, mock_print, mock_exit):
        """Test loading iCS file with exception."""
        load_ics_file("error.ics")

        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_once()


class TestGroupEventsByMonth:
    """Test group_events_by_month function."""

    def test_group_events_by_month_basic(self):
        """Test basic event grouping by month."""
        # Create mock events
        event1 = Mock()
        event1.begin.date.return_value = datetime.date(2025, 1, 15)

        event2 = Mock()
        event2.begin.date.return_value = datetime.date(2025, 1, 20)

        event3 = Mock()
        event3.begin.date.return_value = datetime.date(2025, 2, 10)

        events = [event1, event2, event3]

        result = group_events_by_month(events)

        assert (2025, 1) in result
        assert (2025, 2) in result
        assert len(result[(2025, 1)]) == 2
        assert len(result[(2025, 2)]) == 1

    def test_group_events_by_month_no_begin(self):
        """Test event grouping with events that have no begin date."""
        event_no_begin = Mock()
        event_no_begin.begin = None

        valid_event = Mock()
        valid_event.begin.date.return_value = datetime.date(2025, 1, 15)

        events = [event_no_begin, valid_event]

        result = group_events_by_month(events)

        assert (2025, 1) in result
        assert len(result[(2025, 1)]) == 1

    def test_group_events_by_month_empty(self):
        """Test event grouping with empty event list."""
        result = group_events_by_month([])
        assert result == {}


class TestGenerateMonthlyCalendar:
    """Test generate_monthly_calendar function."""

    def test_generate_monthly_calendar_basic(self):
        """Test basic monthly calendar generation."""
        # Create mock event for January 15th
        event = Mock()
        event.begin.date.return_value = datetime.date(2025, 1, 15)

        result = generate_monthly_calendar(2025, 1, [event])

        assert "January 2025" in result
        assert "Mo Tu We Th Fr Sa Su" in result

    def test_generate_monthly_calendar_no_events(self):
        """Test monthly calendar generation with no events."""
        result = generate_monthly_calendar(2025, 1, [])

        assert "January 2025" in result
        assert "Mo Tu We Th Fr Sa Su" in result

    def test_generate_monthly_calendar_different_month(self):
        """Test monthly calendar generation for different month."""
        event = Mock()
        event.begin.date.return_value = datetime.date(2025, 2, 10)

        result = generate_monthly_calendar(2025, 2, [event])

        assert "February 2025" in result


class TestGenerateEventListing:
    """Test generate_event_listing function."""

    def test_generate_event_listing_basic(self):
        """Test basic event listing generation."""
        event = Mock()
        event.begin.date.return_value = datetime.date(2025, 1, 15)
        event.name = "Test Event 🗑️"
        event.location = None
        event.description = None

        result = generate_event_listing([event])

        assert "Wednesday, January 15, 2025" in result  # 2025-01-15 is a Wednesday
        assert "Test Event" in result

    def test_generate_event_listing_empty(self):
        """Test event listing with no events."""
        result = generate_event_listing([])
        assert "No events found" in result

    def test_generate_event_listing_with_location(self):
        """Test event listing with location information."""
        event = Mock()
        event.begin.date.return_value = datetime.date(2025, 1, 15)
        event.name = "Test Event"
        event.location = "Test Location"
        event.description = None

        result = generate_event_listing([event])

        assert "Test Location" in result

    def test_generate_event_listing_no_begin(self):
        """Test event listing with event that has no begin date."""
        event_no_begin = Mock()
        event_no_begin.begin = None

        valid_event = Mock()
        valid_event.begin.date.return_value = datetime.date(2025, 1, 15)
        valid_event.name = "Valid Event"
        valid_event.location = None
        valid_event.description = None

        result = generate_event_listing([event_no_begin, valid_event])

        assert "Valid Event" in result


class TestGenerateSummaryStatistics:
    """Test generate_summary_statistics function."""

    def test_generate_summary_statistics_basic(self):
        """Test basic summary statistics generation."""
        event1 = Mock()
        event1.begin.date.return_value = datetime.date(2025, 1, 15)
        event1.name = "Residual waste 🗑️"

        event2 = Mock()
        event2.begin.date.return_value = datetime.date(2025, 1, 20)
        event2.name = "Paper collection 📄"

        result = generate_summary_statistics([event1, event2])

        assert "Calendar Summary" in result
        assert "Total events:" in result and "2" in result  # Allow for formatting
        assert "2025-01-15" in result
        assert "2025-01-20" in result

    def test_generate_summary_statistics_empty(self):
        """Test summary statistics with no events."""
        result = generate_summary_statistics([])
        assert "No events to analyze" in result

    def test_generate_summary_statistics_no_begin(self):
        """Test summary statistics with events that have no begin date."""
        event_no_begin = Mock()
        event_no_begin.begin = None

        result = generate_summary_statistics([event_no_begin])

        # When there are events but no valid begin dates, we get 0 total events
        assert "Total events:" in result and "0" in result


class TestViewIcsFile:
    """Test view_ics_file function."""

    @patch("waste_cal.ics_viewer.viewer.load_ics_file")
    @patch("waste_cal.ics_viewer.viewer.generate_summary_statistics")
    @patch("waste_cal.ics_viewer.viewer.generate_event_listing")
    @patch("waste_cal.ics_viewer.viewer.group_events_by_month")
    @patch("waste_cal.ics_viewer.viewer.generate_monthly_calendar")
    def test_view_ics_file_full_format(
        self, mock_monthly_cal, mock_group_events, mock_listing, mock_summary, mock_load
    ):
        """Test view_ics_file with full format."""
        mock_cal = Mock()
        mock_event = Mock()
        mock_event.begin.date.return_value = datetime.date(2025, 1, 15)
        mock_cal.events = [mock_event]
        mock_load.return_value = mock_cal

        mock_summary.return_value = "Summary content"
        mock_listing.return_value = "Listing content"
        mock_group_events.return_value = {(2025, 1): [mock_event]}
        mock_monthly_cal.return_value = "Monthly calendar content"

        result = view_ics_file("test.ics", "full")

        assert "test.ics" in result
        assert "Summary content" in result
        assert "Listing content" in result

    @patch("waste_cal.ics_viewer.viewer.load_ics_file")
    def test_view_ics_file_no_events(self, mock_load):
        """Test view_ics_file with no events."""
        mock_cal = Mock()
        mock_cal.events = []
        mock_load.return_value = mock_cal

        result = view_ics_file("test.ics", "full")

        assert "No events found in calendar" in result

    @patch("waste_cal.ics_viewer.viewer.load_ics_file")
    @patch("waste_cal.ics_viewer.viewer.generate_summary_statistics")
    def test_view_ics_file_summary_format(self, mock_summary, mock_load):
        """Test view_ics_file with summary format only."""
        mock_cal = Mock()
        mock_event = Mock()
        mock_cal.events = [mock_event]
        mock_load.return_value = mock_cal

        mock_summary.return_value = "Summary content"

        result = view_ics_file("test.ics", "summary")

        assert "Summary content" in result


class TestGenerateCalendarView:
    """Test generate_calendar_view function."""

    @patch("waste_cal.ics_viewer.viewer.view_ics_file")
    def test_generate_calendar_view(self, mock_view):
        """Test generate_calendar_view calls view_ics_file with full format."""
        mock_view.return_value = "Calendar view"

        result = generate_calendar_view("test.ics")

        assert result == "Calendar view"
        mock_view.assert_called_once_with("test.ics", "full")
