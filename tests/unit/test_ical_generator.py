"""Unit tests for ical_generator module."""

import os
import tempfile
from datetime import date, timedelta

import pytest

from ics import Calendar
from ics.alarm import DisplayAlarm
from waste_cal.calendar_processor import CalendarData
from waste_cal.ical_generator import generate_all_ical_files, generate_ical_file
from waste_cal.waste_types import Languages, WasteType


def create_mock_calendar_data() -> CalendarData:
    """Create mock calendar data for testing."""
    calendar_data = CalendarData()

    # Add some test dates with different waste types
    test_date_1 = date(2025, 1, 15)  # Regular collection
    test_date_2 = date(2025, 1, 20)  # Special collection
    test_date_3 = date(2025, 1, 25)  # Mixed collection

    calendar_data.add_collection(test_date_1, WasteType.RESIDUAL)
    calendar_data.add_collection(test_date_1, WasteType.ORGANIC)
    calendar_data.add_collection(test_date_2, WasteType.ELECTRIC)
    calendar_data.add_collection(test_date_2, WasteType.BULKY)
    calendar_data.add_collection(test_date_3, WasteType.PAPER)
    calendar_data.add_collection(test_date_3, WasteType.HEDGE)

    return calendar_data


class TestGenerateIcalFile:
    """Test generate_ical_file function."""

    def test_generate_ical_file_creates_file(self):
        """Test that generate_ical_file creates a valid iCal file."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_ical_file(calendar_data, Languages.EN, 2025, temp_dir)

            # Check file was created
            assert os.path.exists(filepath)
            assert filepath.endswith("waste-en.ics")

            # Check file content is valid iCal
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
                assert "BEGIN:VCALENDAR" in content
                assert "END:VCALENDAR" in content

    def test_generate_ical_file_contains_events(self):
        """Test that generated iCal file contains expected events."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_ical_file(calendar_data, Languages.EN, 2025, temp_dir)

            # Parse the generated calendar
            with open(filepath, encoding="utf-8") as f:
                calendar = Calendar(f.read())

            # Should have 6 events (one for each waste type on each date)
            assert len(calendar.events) == 6

            # Check event properties
            for event in calendar.events:
                assert event.name  # Should have a name
                assert event.description  # Should have a description
                assert event.location == "Niederanven, Luxembourg"
                assert event.all_day  # Should be all-day events

    def test_generate_ical_file_alarms_for_regular_collections(self):
        """Test that alarms are added only for regular collection types."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_ical_file(calendar_data, Languages.EN, 2025, temp_dir)

            # Parse the generated calendar
            with open(filepath, encoding="utf-8") as f:
                calendar = Calendar(f.read())

            # Count events with and without alarms
            events_with_alarms = []
            events_without_alarms = []

            for event in calendar.events:
                if event.alarms:
                    events_with_alarms.append(event)
                else:
                    events_without_alarms.append(event)

            # Should have 3 events with alarms (RESIDUAL, ORGANIC, PAPER)
            assert len(events_with_alarms) == 3
            # Should have 3 events without alarms (ELECTRIC, BULKY, HEDGE)
            assert len(events_without_alarms) == 3

            # Check alarm properties
            for event in events_with_alarms:
                assert len(event.alarms) == 1
                alarm = list(event.alarms)[0]
                assert isinstance(alarm, DisplayAlarm)
                assert alarm.display_text  # Should have alarm message
                # Should trigger the day before at 20:30
                assert alarm.trigger == timedelta(days=-1, hours=20, minutes=30)

    @pytest.mark.parametrize(
        "language,expected_suffix",
        [
            (Languages.LU, "lu"),
            (Languages.FR, "fr"),
            (Languages.EN, "en"),
        ],
    )
    def test_generate_ical_file_language_specific_filenames(self, language: Languages, expected_suffix: str):
        """Test that files are named correctly for each language."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_ical_file(calendar_data, language, 2025, temp_dir)

            expected_filename = f"waste-{expected_suffix}.ics"
            assert filepath.endswith(expected_filename)

    @pytest.mark.parametrize("language", [Languages.LU, Languages.FR, Languages.EN])
    def test_generate_ical_file_language_specific_content(self, language: Languages):
        """Test that event content is localized for each language."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_ical_file(calendar_data, language, 2025, temp_dir)

            # Parse the generated calendar
            with open(filepath, encoding="utf-8") as f:
                calendar = Calendar(f.read())

            # Check that events contain language-specific descriptions
            for event in calendar.events:
                # Event name should contain waste type description in the specified language
                # We can't easily test the exact content without knowing which waste type
                # each event represents, but we can check basic structure
                assert event.name  # Should have a name
                assert event.description.startswith("Waste collection:")

                # Check alarm messages for events that have alarms
                if event.alarms:
                    alarm = list(event.alarms)[0]
                    # Alarm message should be in the correct language
                    if language == Languages.LU:
                        assert "Moien!" in alarm.display_text
                    elif language == Languages.FR:
                        assert "Rappel:" in alarm.display_text
                    elif language == Languages.EN:
                        assert "Reminder:" in alarm.display_text

    def test_generate_ical_file_creates_output_directory(self):
        """Test that output directory is created if it doesn't exist."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "new_directory")
            assert not os.path.exists(output_dir)

            filepath = generate_ical_file(calendar_data, Languages.EN, 2025, output_dir)

            # Directory should be created
            assert os.path.exists(output_dir)
            assert os.path.exists(filepath)


class TestGenerateAllIcalFiles:
    """Test generate_all_ical_files function."""

    def test_generate_all_ical_files_creates_all_languages(self):
        """Test that generate_all_ical_files creates files for all languages."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepaths = generate_all_ical_files(calendar_data, 2025, temp_dir)

            # Should create 3 files (one for each language)
            assert len(filepaths) == 3

            # Check that all files exist and have correct names
            expected_files = ["waste-lu.ics", "waste-fr.ics", "waste-en.ics"]
            actual_files = [os.path.basename(fp) for fp in filepaths]

            for expected_file in expected_files:
                assert expected_file in actual_files

            # Check that all files exist
            for filepath in filepaths:
                assert os.path.exists(filepath)

    def test_generate_all_ical_files_returns_correct_paths(self):
        """Test that generate_all_ical_files returns correct file paths."""
        calendar_data = create_mock_calendar_data()

        with tempfile.TemporaryDirectory() as temp_dir:
            filepaths = generate_all_ical_files(calendar_data, 2025, temp_dir)

            # All paths should be in the specified directory
            for filepath in filepaths:
                assert filepath.startswith(temp_dir)
                assert filepath.endswith(".ics")


class TestAlarmIntegration:
    """Integration tests for alarm functionality with real calendar generation."""

    @pytest.mark.integration
    def test_end_to_end_alarm_generation(self):
        """Integration test: Generate real calendar with alarms and verify output."""
        # Create a realistic calendar data scenario
        calendar_data = CalendarData()

        # Add collections for a full week with mixed waste types
        base_date = date(2025, 3, 10)  # Monday

        # Monday: Regular collections (should have alarms)
        calendar_data.add_collection(base_date, WasteType.RESIDUAL)
        calendar_data.add_collection(base_date, WasteType.ORGANIC)

        # Wednesday: Paper collection (should have alarm)
        calendar_data.add_collection(base_date + timedelta(days=2), WasteType.PAPER)

        # Friday: Special collections (should NOT have alarms)
        calendar_data.add_collection(base_date + timedelta(days=4), WasteType.ELECTRIC)
        calendar_data.add_collection(base_date + timedelta(days=4), WasteType.BULKY)

        # Saturday: Mixed collection
        calendar_data.add_collection(base_date + timedelta(days=5), WasteType.GLASS)  # Should have alarm
        calendar_data.add_collection(base_date + timedelta(days=5), WasteType.HEDGE)  # Should NOT have alarm

        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate calendars for all languages
            filepaths = generate_all_ical_files(calendar_data, 2025, temp_dir)

            # Verify all files were created
            assert len(filepaths) == 3

            # Test each language file
            for filepath in filepaths:
                assert os.path.exists(filepath)

                # Parse and verify the calendar
                with open(filepath, encoding="utf-8") as f:
                    calendar = Calendar(f.read())

                # Should have 7 events total
                assert len(calendar.events) == 7

                # Count events with alarms (should be 4: RESIDUAL, ORGANIC, PAPER, GLASS)
                events_with_alarms = [e for e in calendar.events if e.alarms]
                events_without_alarms = [e for e in calendar.events if not e.alarms]

                assert len(events_with_alarms) == 4
                assert len(events_without_alarms) == 3

                # Verify alarm properties for all alarmed events
                for event in events_with_alarms:
                    assert len(event.alarms) == 1
                    alarm = list(event.alarms)[0]
                    assert isinstance(alarm, DisplayAlarm)
                    assert alarm.display_text
                    assert alarm.trigger == timedelta(days=-1, hours=20, minutes=30)

                    # Verify language-specific alarm messages
                    if "waste-lu.ics" in filepath:
                        assert "Moien!" in alarm.display_text
                        assert "muer ofgeholl" in alarm.display_text
                    elif "waste-fr.ics" in filepath:
                        assert "Rappel:" in alarm.display_text
                        assert "collecté demain" in alarm.display_text
                    elif "waste-en.ics" in filepath:
                        assert "Reminder:" in alarm.display_text
                        assert "collected tomorrow" in alarm.display_text
